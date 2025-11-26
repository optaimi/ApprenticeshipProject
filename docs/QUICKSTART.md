# Product Validation System - Quick Start Guide

This guide helps you get the full system (backend + frontend) running locally.

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- pip (Python package manager)

## Quick Setup (Windows PowerShell)

Run this one command from the project root:

```powershell
.\setup.ps1
```

This will:
- Create and activate a Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Show next steps

Then skip to [Step 3](#step-3-using-the-application) to start testing.

---

## Manual Setup

## Architecture

```
┌─────────────────┐
│   Next.js App   │ (http://localhost:3000)
│   (Frontend)    │
└────────┬────────┘
         │ REST API
         ↓
┌─────────────────┐
│   FastAPI       │ (http://localhost:8000)
│   (Backend)     │
└────────┬────────┘
         │ Python modules
         ↓
┌─────────────────┐
│ validation_engine.py
│ llm_explanations.py
│ ho_products_dummy_200.csv
└─────────────────┘
```

## Step 1: Backend Setup

### 1.1 Create and Activate Python Virtual Environment

From project root:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate virtual environment (Windows CMD)
.venv\Scripts\activate.bat

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 1.2 Install Python Dependencies

With venv activated:

```bash
pip install -r requirements.txt
```

This installs:
- fastapi, uvicorn (API framework)
- pandas, scikit-learn (data processing)
- openai (optional, for AI explanations)
- streamlit (for legacy UI, not needed for new frontend)

### 1.3 Start FastAPI Server

From project root (with venv activated):

```bash
python api_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test the API:**
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

The API will:
- Load `validation_engine.py` and `ho_products_dummy_200.csv` on startup
- Build the TF-IDF model
- Listen for requests on `/api/validate`, `/api/submit`, etc.

**Keep this terminal running!** (Don't close or deactivate venv while testing)

**To deactivate venv later:**
```bash
deactivate
```

## Step 2: Frontend Setup

### 2.1 Install Node Dependencies

In a new terminal, navigate to the frontend:

```bash
cd frontend
npm install
```

This installs:
- Next.js 14+
- React, TypeScript
- Tailwind CSS
- react-hook-form
- framer-motion

### 2.2 Start Development Server

```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Step 3: Using the Application

### User Submission Form (`/`)

1. Enter a product name (e.g., "Coca-Cola 1L")
2. Select a category from dropdown
3. Enter a price in GBP
4. Select age verification (Yes/No)
5. **Blur any field** to trigger real-time validation
6. View validation feedback below the form
7. Click **Submit Product** if all looks good

**Validation Response:**
- ✓ **Pass**: Auto-approved, 15-20 minute processing
- ⚠ **Warning**: HO review needed (optional notes)
- ✕ **Hard Stop**: Must fix before submitting

### Head Office View (`/ho-view`)

1. View pending submissions needing review
2. Click **Approve** to auto-approve
3. Click **Deny** to reject
4. View approved submissions in the right column
5. Page auto-refreshes every 10 seconds

## Important Reminders Before Testing

✅ **Backend terminal**: venv activated, FastAPI running on localhost:8000  
✅ **Frontend terminal**: npm dev running on localhost:3000  
✅ **Both running simultaneously**: Keep both terminal windows open

## Common Test Scenarios

### Test 1: Valid Product (Auto-Approve)

```
Product Name: Coca-Cola 1L
Category: Soft drinks
Price: 1.85
Age Verified: No
```

Expected: ✓ All pass → "Ready for automatic approval"

### Test 2: Price Warning

```
Product Name: Sprite 1L
Category: Soft drinks
Price: 5.00
Age Verified: No
```

Expected: ⚠ Price warning → Flagged for HO review

### Test 3: Hard Stop (Age Policy)

```
Product Name: Budweiser 440ml
Category: Alcohol
Price: 3.00
Age Verified: No  ← Should be Yes
```

Expected: ✕ Hard stop → "Age verification must be Yes"

### Test 4: Category Mismatch

```
Product Name: Gordon's Gin 700ml
Category: Soft drinks  ← Wrong category
Price: 15.00
Age Verified: Yes
```

Expected: ⚠ Warning → Suggest correct category

## Stopping the Services

**Backend:** Press `Ctrl+C` in the API terminal (venv stays active until terminal closes or `deactivate` is called)

**Frontend:** Press `Ctrl+C` in the dev server terminal

To deactivate venv: `deactivate`

---

**Note**: For more venv issues and explanations, see **VENV_GUIDE.md**

## Troubleshooting

### Frontend can't connect to API

**Error:** "API Server Offline"

**Fix:**
1. Ensure FastAPI is running: `python api_server.py`
2. Verify it's on http://localhost:8000
3. Check firewall isn't blocking localhost:8000

### Port already in use

**Backend (8000):**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# Or use netstat on Windows
```

**Frontend (3000):**
```bash
npm run dev -- -p 3001
```

### Tailwind styles not applying

```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Form validation not triggering

- Make sure you **blur** (click away) from fields, not just type
- Validation happens on blur, not on keystroke
- Fill all required fields: Product Name, Category, Price

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if API is online |
| `/api/categories` | GET | Get list of product categories |
| `/api/validate` | POST | Validate a product submission |
| `/api/submit` | POST | Store a validated submission |
| `/api/submissions` | GET | Get all submissions (pending + approved) |
| `/api/submissions/{id}/approve` | POST | Approve a pending submission |
| `/api/submissions/{id}/deny` | POST | Deny a pending submission |

## Next Steps

- **Test**: Use the scenarios above to verify all flows work
- **Customize**: Update HO products CSV or validation rules
- **Deploy**: See frontend/README.md and IMPLEMENTATION_PLAN.md for production setup
- **Extend**: Add database persistence, authentication, or additional validation logic

## File Structure

```
ApprenticeshipProject/
├── api_server.py              ← FastAPI backend
├── validation_engine.py       ← Core validation logic (unchanged)
├── llm_explanations.py        ← AI explanations (unchanged)
├── ho_products_dummy_200.csv  ← HO reference data
├── requirements.txt           ← Python dependencies
├── IMPLEMENTATION_PLAN.md     ← Detailed implementation notes
├── QUICKSTART.md              ← This file
└── frontend/
    ├── package.json           ← Node dependencies
    ├── app/
    │   ├── page.tsx           ← User submission form
    │   ├── ho-view/page.tsx   ← HO dashboard
    │   └── ...
    ├── components/
    ├── lib/
    ├── types/
    └── README.md
```

## Support

- Check IMPLEMENTATION_PLAN.md for technical details
- See frontend/README.md for frontend-specific documentation
- Review api_server.py for API implementation details
- Refer to validation_engine.py comments for validation logic

Happy validating! 🚀
