# JH Product Validation – Demo

Proof-of-concept tool for validating store-submitted products against a head office (HO) product file.

The demo simulates:

- Stores submitting new products (name, category, price, age check)
- Validation against existing HO data using similarity over product names
- Rules for category, pricing, and age verification
- AI explanations using GPT-4.1 nano
- A simple web UI built with Streamlit

---

## 1. Project structure

```text
product-validation-demo/
  app.py                  # Streamlit UI
  validation_engine.py    # Core validation logic
  llm_explanations.py     # GPT-4.1 nano explanation layer
  ho_products_dummy_200.csv
  requirements.txt
  README.md

---

## 2. Prerequisites

- Python 3.10 or later
- An OpenAI API key (for GPT-4.1 nano explanations)
- Git (optional, if cloning from a repo)

---

## 3. Installation

cd product-validation-demo

# Create a virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Or on Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

Make sure ho_products_dummy_200.csv sits in the project root.

requirements.txt:
streamlit
pandas
scikit-learn
openai

---

## 4. OpenAI configuration (GPT-4.1 nano)

Set your OpenAI API key in the environment so the SDK can pick it up:
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."

# Linux/macOS (bash)
export OPENAI_API_KEY="sk-..."

The app uses the official OpenAI Python client and the gpt-4.1-nano model for explanations only.
Validation decisions remain fully rule-based.

---

## 5. Running the demo

From the project folder, with the virtual environment activated:

streamlit run app.py

Streamlit prints a local URL, for example:
http://localhost:8501

Open that in a browser.

You will see:
- A form for product name, category, price, and age verification
- A structured validation result
- A table of similar HO products
- An optional AI explanation section (toggle on/off)

---

## 6. How the validation works

The engine in validation_engine.py:
    1. Loads HO data
        - Reads ho_products_dummy_200.csv into a pandas DataFrame.
        - Normalises missing values for product name and category.
    2. Builds a similarity model
        - Uses TF–IDF over ProductName with unigrams and bigrams.
        - Uses cosine similarity (via linear_kernel) to find the most similar HO products for any new submission.
    3. Derives signals from nearest neighbours
        - Category
            - Sums similarity scores per HO category.
            - Picks the category with the highest total similarity.
            - Calculates a confidence score as the share of total similarity.
        - Price
            - Takes the median price of similar products.
            - Builds a simple price band (±25% around the median).
        - Age verification
            - Looks at the most common age-check setting among similar products.
            - Derives a confidence score from the ratio of “yes” vs “no”.
    4. Applies rules
        - Category:
            - Matches store category vs predicted HO category.
            - Uses confidence thresholds to return pass or warning.
        - Price:
            - Flags prices that are too low or zero.
            - Uses percentage difference from the median to return pass, warning, or hard_stop.
        - Age verification:
            - Uses simple keyword-based policy rules (e.g. alcohol words).
            - Combines policy and HO pattern to return pass, warning, or hard_stop.
    5. Combines decisions
        - If any field is hard_stop → overall: Requires correction before submission.
        - Else if any field is warning → overall: Submitted with warnings; HO will review.
        - Else → overall: Ready for automatic approval.

The Streamlit app in app.py just calls validate_product(...) and displays:
- Overall status
- Category, price, and age-check sections
- Similar HO products table

---

## 7. GPT-4.1 nano explanations

The module llm_explanations.py adds an explanation layer on top of the rules engine:
- It takes:
    - The original submission (name, category, price, age flag)
    - The structured result from validate_product(...)
- It builds a prompt that describes:
    -The submission
    - The decisions and messages for category, price, and age check
- It asks GPT-4.1 nano to produce markdown output with:
### For the store
- Bullet points...

### For head office
- Bullet points...

- It does not change any decisions. It only explains the existing result.

In the UI:
- A toggle labelled Generate AI explanation (GPT-4.1 nano) controls whether the app calls the model.
- If the call fails (no key, network issue), the app shows a warning and still displays the rule-based result.

---

## 8. Function reference
    # 8.1 validation_engine.py

df: pandas.DataFrame
- Description:
  Loaded HO product data from ho_products_dummy_200.csv.
- Usage:
    - Used to build the TF–IDF matrix.
    - Imported into app.py to populate the category dropdown.

get_neighbours(product_name: str, top_k: int = 15) -> pandas.DataFrame
- Description:
  Finds the top_k most similar HO products to the given product_name.
- Parameters:
    - product_name: New product name from the store.
    - top_k: Number of neighbours to return.
- Returns:
  DataFrame of neighbours with an extra similarity column (float).

infer_category(neighbours: pandas.DataFrame) -> tuple[str | None, float]
- Description:
  Infers the most likely HO category from similar products.
- Logic:
    - Groups neighbours by Category.
    - Sums similarity per category.
    - Picks the highest and computes a confidence ratio.
- Returns:
    - predicted_category (or None if no data).
    - confidence in [0, 1].

infer_price_band(neighbours: pandas.DataFrame) -> tuple[float | None, float | None, float | None]
- Description:
  Estimates a typical price and a reasonable band for the product.
- Logic:
    - Takes the median of PriceGBP from neighbours.
    - Sets lower = median * 0.75, upper = median * 1.25.
- Returns:
    - median price (float or None).
    - lower bound (float or None).
    - upper bound (float or None).

infer_age_flag(neighbours: pandas.DataFrame) -> tuple[str | None, float]
- Description:
  Infers the typical age-verification setting for similar products.
- Logic:
    - Normalises AgeVerificationRequired to lower-case strings.
    - Computes the share of "yes" among neighbours.
    - Predicts "Yes" if yes_ratio >= 0.5, otherwise "No".
    - Confidence scales with distance from 0.5 (0–1).
- Returns:
    - predicted_flag ("Yes", "No", or None).
    - confidence in [0, 1].

requires_age_verification_by_policy(product_name: str, category: str) -> bool
- Description:
  Simple policy check based on category and name keywords.
- Logic:
    - If the category contains "alcohol" → True.
    - If the name contains any alcohol keyword (beer, cider, wine, vodka, etc.) → True.
- Returns:
    - True if policy suggests an age check is required; otherwise False.

classify_category(store_cat: str, predicted_cat: str | None, confidence: float) -> tuple[str, str]
- Description:
  Compares the store’s category to the predicted HO category.
- Logic:
    - If no prediction → "pass", generic acceptance message.
    - If store_cat == predicted_cat → "pass".
    - Else, if confidence >= 0.7 → "warning" with strong suggestion.
    - Else → "warning" with softer wording.
- Returns:
    - decision: "pass" or "warning".
    - message: Human-readable explanation.

classify_price(price: float, median: float | None, lower: float | None, upper: float | None) -> tuple[str, str]
- Description:
  Validates submitted price against the typical HO price band.
- Logic:
    - If median is None → "pass", accept price.
    - If price <= 0 → "hard_stop".
    - Calculates percentage difference from the median:
        - |diff| <= 25% → "pass".
        - 25% < |diff| <= 50% → "warning".
        - |diff| > 50% → "hard_stop".
- Returns:
    - decision: "pass", "warning", or "hard_stop".
    - message: Explanation of how the price compares to typical HO prices.

classify_age_flag(product_name: str, category: str, store_flag: str, predicted_flag: str | None, confidence: float) -> tuple[str, str]
- Description:
  Validates the age-verification flag using policy and HO patterns.
- Logic:
    - Normalises store_flag and predicted_flag to "Yes" / "No".
    - If policy says age check is required and store set "No" → "hard_stop".
    - If no prediction → "pass".
    - If store matches predicted → "pass".
    - Else, if confidence >= 0.7 → "warning" with strong suggestion.
    - Else → "warning" with softer message.
- Returns:
    - decision: "pass", "warning", or "hard_stop".
    - message: Explanation.

validate_product(product_name: str, category: str, price: float, age_flag: str) -> dict
- Description:
  Main public API for the validation engine.
- Logic:
    - Calls get_neighbours.
    - Runs infer_category, infer_price_band, infer_age_flag.
    - Applies classify_category, classify_price, classify_age_flag.
    - Derives an overall status based on field-level decisions.
- Returns:
  A dictionary with keys:
    - "neighbours": DataFrame of similar HO products.
    - "category": dict with decision, predicted, confidence, message.
    - "price": dict with decision, median, lower, upper, message.
    - "age_verification": dict with decision, predicted, confidence, message.
    - "overall": human-readable overall status string.

This function is what app.py calls.

    # 8.2 llm_explanations.py

build_explanation_prompt(submission: dict, result: dict) -> str
- Description:
  Builds a markdown-oriented prompt for GPT-4.1 nano using the submission and validation result.
- Parameters:
    - submission: dict with keys "name", "category", "price", "age_flag".
    - result: dict returned from validate_product(...).
- Returns:
  A formatted prompt string that describes the case and asks for:

### For the store
- ...

### For head office
- ...

generate_explanation(submission: dict, result: dict) -> str
- Description:
  Calls GPT-4.1 nano to turn the rule-based result into a human explanation.
- Logic:
    - Builds the prompt using build_explanation_prompt.
    - Uses the OpenAI client:
response = client.responses.create(
    model="gpt-4.1-nano",
    input=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": prompt},
    ],
)

    - Extracts the plain text via response.output_text.
- Returns:
  A markdown string ready to render with st.markdown(...).

    # 8.3 app.py (high-level)

app.py does not expose reusable functions; it wires everything together:
- Imports:
from validation_engine import df, validate_product
from llm_explanations import generate_explanation

- Builds a Streamlit form for:
    - product_name (text input)
    - category (select box, from df["Category"].unique())
    - price (number input)
    - age_flag (select box: Yes/No)
- On submit:
    - Calls validate_product(...).
    - Displays:
        - Overall status
        - Section per field (category, price, age)
        - Similar HO products in an expander
    - Optional:
        - Uses a toggle to call generate_explanation(...).
        - Renders the markdown explanation under AI explanation.

This keeps the UI thin and makes the engine and LLM layers easy to reuse in other front ends (e.g. FastAPI, Gradio, or a React app later).