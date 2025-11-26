"""
FastAPI wrapper for the validation engine.
Provides REST endpoints for the Next.js frontend.
"""
import os  
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from google.cloud import storage 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from validation_engine import validate_product, df

# Storage Configuration
APP_ENV = os.getenv("APP_ENV", "local") # Defaults to 'local' if not set
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME") # To be updated from Google Cloud
DATA_FILENAME = "submissions.json"


# ===== Data Models =====

class ProductInput(BaseModel):
    product_name: str
    category: str
    price: float
    age_flag: str


class FieldValidation(BaseModel):
    decision: str  # "pass", "warning", "hard_stop"
    message: str
    predicted: Optional[str] = None
    confidence: Optional[float] = None


class PriceValidation(BaseModel):
    decision: str
    message: str
    median: Optional[float] = None
    lower: Optional[float] = None
    upper: Optional[float] = None


class AgeVerificationValidation(BaseModel):
    decision: str
    message: str
    predicted: Optional[str] = None
    confidence: Optional[float] = None


class ValidationResult(BaseModel):
    category: FieldValidation
    price: PriceValidation
    age_verification: AgeVerificationValidation
    overall: str


class SubmissionData(BaseModel):
    product: ProductInput
    validation: dict  # Raw validation result
    accepted_changes: list = []
    notes: Optional[str] = None
    flagged: bool = False


class SubmissionResponse(BaseModel):
    id: str
    timestamp: str
    product: ProductInput
    validation: dict
    accepted_changes: list
    notes: Optional[str] = None
    status: str  # "pending", "approved", "denied"
    flagged: bool


# ===== In-Memory Storage =====
submissions: dict = {}  # id -> submission dict
next_submission_id = 1


def load_submissions_from_file():
    """Load submissions from Local File or Google Cloud Storage."""
    global submissions, next_submission_id
    
    data = None

    if APP_ENV == "cloud":
        # --- CLOUD MODE ---
        try:
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(DATA_FILENAME)
            
            if blob.exists():
                json_data = blob.download_as_text()
                data = json.loads(json_data)
                print(f"Loaded data from GCS bucket: {GCS_BUCKET_NAME}")
            else:
                print("No data file found in GCS, starting fresh.")
                data = {"submissions": []}
        except Exception as e:
            print(f"Error loading from GCS: {e}")
            data = {"submissions": []}
            
    else:
        # --- LOCAL MODE ---
        submissions_file = Path(DATA_FILENAME)
        if submissions_file.exists():
            try:
                with open(submissions_file, "r") as f:
                    data = json.load(f)
                    print("Loaded data from local file.")
            except Exception:
                data = {"submissions": []}

    # Process the loaded data (same for both modes)
    if data:
        submissions = {sub["id"]: sub for sub in data.get("submissions", [])}
        # Calculate next ID safely
        if submissions:
            ids = [int(sub["id"]) for sub in submissions.values() if str(sub["id"]).isdigit()]
            next_submission_id = max(ids) + 1 if ids else 1
        else:
            next_submission_id = 1


def save_submissions_to_file():
    """Persist submissions to Local File or Google Cloud Storage."""
    data_to_save = {"submissions": list(submissions.values())}
    
    if APP_ENV == "cloud":
        # --- CLOUD MODE ---
        try:
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(DATA_FILENAME)
            
            blob.upload_from_string(
                json.dumps(data_to_save, indent=2),
                content_type='application/json'
            )
            print(f"Saved to GCS bucket: {GCS_BUCKET_NAME}")
        except Exception as e:
            print(f"Error saving to GCS: {e}")
            
    else:
        # --- LOCAL MODE ---
        submissions_file = Path(DATA_FILENAME)
        try:
            with open(submissions_file, "w") as f:
                json.dump(data_to_save, f, indent=2)
            print("Saved to local file.")
        except Exception as e:
            print(f"Error saving locally: {e}")


# ===== FastAPI App =====

app = FastAPI(title="Product Validation API")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load submissions from file on startup."""
    load_submissions_from_file()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/categories")
def get_categories():
    """Get list of categories from HO data."""
    categories = sorted(df["Category"].unique().tolist())
    return {"categories": categories}


@app.post("/api/validate")
def validate_endpoint(product: ProductInput):
    """
    Validate a product submission.
    
    Returns structured validation result matching validation_engine.py output.
    """
    try:
        result = validate_product(
            product_name=product.product_name,
            category=product.category,
            price=product.price,
            age_flag=product.age_flag
        )
        
        # Remove DataFrame from result for JSON serialization
        result_copy = result.copy()
        neighbours_df = result_copy.pop("neighbours")
        
        # Convert neighbours DataFrame to list of dicts
        neighbours = neighbours_df[[
            "ProductName", "Category", "PriceGBP", "AgeVerificationRequired", "similarity"
        ]].to_dict("records")
        
        result_copy["neighbours"] = neighbours
        
        return result_copy
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/submit")
def submit_endpoint(submission: SubmissionData):
    """
    Submit a product for storage.
    
    Returns submission_id and status.
    """
    global next_submission_id, submissions
    
    try:
        submission_id = str(next_submission_id)
        next_submission_id += 1
        
        submission_dict = {
            "id": submission_id,
            "timestamp": datetime.utcnow().isoformat(),
            "product": submission.product.dict(),
            "validation": submission.validation,
            "accepted_changes": submission.accepted_changes,
            "notes": submission.notes,
            "status": "pending" if submission.flagged else "approved",
            "flagged": submission.flagged,
        }
        
        submissions[submission_id] = submission_dict
        save_submissions_to_file()
        
        return {
            "id": submission_id,
            "status": submission_dict["status"],
            "timestamp": submission_dict["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/submissions")
def get_submissions():
    """
    Get all submissions grouped by status.
    
    Returns pending and approved submissions.
    """
    pending = [sub for sub in submissions.values() if sub["status"] == "pending"]
    approved = [sub for sub in submissions.values() if sub["status"] in ("approved", "denied")]
    
    return {
        "pending": sorted(pending, key=lambda x: x["timestamp"], reverse=True),
        "approved": sorted(approved, key=lambda x: x["timestamp"], reverse=True),
    }


@app.post("/api/submissions/{submission_id}/approve")
def approve_submission(submission_id: str):
    """Approve a pending submission."""
    if submission_id not in submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submissions[submission_id]["status"] = "approved"
    save_submissions_to_file()
    
    return {"status": "approved", "id": submission_id}


@app.post("/api/submissions/{submission_id}/deny")
def deny_submission(submission_id: str, reason: Optional[str] = None):
    """Deny a pending submission."""
    if submission_id not in submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submissions[submission_id]["status"] = "denied"
    if reason:
        submissions[submission_id]["denial_reason"] = reason
    
    save_submissions_to_file()
    
    return {"status": "denied", "id": submission_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
