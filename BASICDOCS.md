## Overview

This repo is a small demo app for validating store-submitted products against a head office (HO) product file. It consists of:
- A Streamlit UI (`app.py`).
- A rule-based validation engine over HO data (`validation_engine.py`).
- An optional GPT-4.1-nano explanation layer (`llm_explanations.py`).
- A dummy HO product CSV (`ho_products_dummy_200.csv`).

The README already documents behaviour and function-level details quite thoroughly; prefer to rely on that file for deeper explanations.


## Common commands

**Quick Note**: Always use a Python virtual environment. See below for setup.

**Environment setup (Python 3.10+)**
- Create venv:
  - `python -m venv .venv`
- Activate venv (PowerShell):
  - `.venv\Scripts\Activate.ps1`
- Activate venv (bash/zsh):
  - `source .venv/bin/activate`
- Create venv:
  - `python -m venv .venv`
- Activate venv (PowerShell):
  - `.venv\Scripts\Activate.ps1`
- Activate venv (bash/zsh):
  - `source .venv/bin/activate`
- Install dependencies (with venv activated):
  - `pip install -r requirements.txt`

**Run the app**
- From the project root, with venv activated:
  - `streamlit run app.py`

**Ad-hoc checks / manual testing**
- There is no formal test suite. To exercise the core engine and LLM layer from the CLI, you can:
  - Open a Python REPL in the venv:
    - `python`
  - Then:
    - `from validation_engine import validate_product`
    - `validate_product("Example beer", "Alcohol", 5.0, "Yes")`
  - For LLM explanations (requires `OPENAI_API_KEY`):
    - `from llm_explanations import generate_explanation`
    - `submission = {"name": "Example beer", "category": "Alcohol", "price": 5.0, "age_flag": "Yes"}`
    - `result = validate_product(**submission)`
    - `generate_explanation(submission, result)`

**OpenAI configuration**
- The app uses `OPENAI_API_KEY` from the environment. Typical setup (do not hard-code keys in code):
  - PowerShell: `$env:OPENAI_API_KEY="sk-..."`
  - bash/zsh: `export OPENAI_API_KEY="sk-..."`


## High-level architecture

### 1. Data and similarity model (`validation_engine.py`)

- Loads `ho_products_dummy_200.csv` into a module-level `pandas` DataFrame `df`.
- Normalises `ProductName` and `Category` columns to avoid nulls.
- Builds a global TF–IDF vectoriser over `ProductName` with unigrams + bigrams, then precomputes a sparse matrix `X` used for similarity.
- This means importing `validation_engine` performs a one-time CSV load and model build; subsequent calls reuse the in-memory structures.

Key responsibilities:
- **Nearest neighbours**
  - `get_neighbours(product_name, top_k=15)` → returns a DataFrame of similar HO products with an extra `similarity` column.
- **Signal extraction** from neighbours:
  - `infer_category(neighbours)` → predicted HO category + confidence (share of similarity mass).
  - `infer_price_band(neighbours)` → median price and a ±25% band.
  - `infer_age_flag(neighbours)` → typical "Yes/No" age flag + confidence derived from distance to 50%.
- **Policy rules**
  - `requires_age_verification_by_policy(product_name, category)` uses an `ALCOHOL_WORDS` list and category string to infer whether age verification is required regardless of HO patterns.
- **Classification** (maps signals to discrete decisions and messages):
  - `classify_category(store_cat, predicted_cat, confidence)` → `"pass"` or `"warning"` with explanation.
  - `classify_price(price, median, lower, upper)` → `"pass" | "warning" | "hard_stop"` based on deviation from typical price and basic sanity checks (e.g. non-positive prices).
  - `classify_age_flag(product_name, category, store_flag, predicted_flag, confidence)` → combines policy and HO pattern into `"pass" | "warning" | "hard_stop"`.
- **Public API**
  - `validate_product(product_name, category, price, age_flag)` orchestrates neighbours → signals → classifications and returns a structured dictionary with:
    - `neighbours` DataFrame.
    - Section dicts for `category`, `price`, and `age_verification` (each includes decision, derived values, and messages).
    - An `overall` string summarising the status (automatic approval, warnings, or required correction).

Design note: `validate_product` is pure with respect to its inputs apart from reading HO data/model from module-level state, which makes it suitable for reuse in other front-ends.


### 2. LLM explanation layer (`llm_explanations.py`)

- Thin wrapper around the OpenAI Python client with a single global `OpenAI()` client instance configured via `OPENAI_API_KEY`.
- This layer **does not change** the validation decision; it only explains it.

Key functions:
- `build_explanation_prompt(submission, result)`
  - Builds a markdown-oriented prompt that embeds:
    - Submission fields (name, category, price, age flag).
    - The full structured `validate_product` output (decisions, messages, predictions, confidence, bands).
  - Enforces:
    - The model must not invent rules or change outcomes.
    - Output structure with two sections: `### For the store` and `### For head office`, each with concise bullets.
- `generate_explanation(submission, result)`
  - Calls `client.responses.create` with `model="gpt-4.1-nano"`.
  - Uses a system message that frames the assistant as explaining validation results.
  - Returns `response.output_text` for direct rendering (markdown) in the UI.

This separation lets you:
- Call the rules engine without the LLM for deterministic behaviour.
- Add or change models/prompts without touching `validation_engine.py` or the UI logic.


### 3. Streamlit UI (`app.py`)

- Imports:
  - `df` and `validate_product` from `validation_engine`.
  - `generate_explanation` from `llm_explanations`.
- Sets page configuration and renders a single-page app.

UI flow:
- Displays a form with:
  - `product_name` (text input).
  - `category` (select box, values derived from `df["Category"].unique()`).
  - `price` (numeric input, non-negative).
  - `age_flag` (select box: `Yes` / `No`).
- On submit:
  - Validates that `product_name` is non-empty.
  - Calls `validate_product(...)` and renders:
    - An overall status block.
    - Detailed sections for category, price, and age verification (decision + message + derived values).
    - An expandable `st.dataframe` view of neighbour HO products (including similarity scores).
- LLM integration:
  - Builds a `submission` dict mirroring the form inputs.
  - Offers a toggle `Generate AI explanation (GPT-4.1 nano)` (default on).
  - When enabled, calls `generate_explanation(submission, result)` and displays the markdown; failures (missing key, network errors) are handled with a generic `st.warning` while keeping the rule-based result available.

The UI layer is intentionally thin: all business logic lives in `validation_engine.py` and `llm_explanations.py`.


## Working on the code

When modifying or extending behaviour, prefer to:
- Add / adjust **rules and model behaviour** in `validation_engine.py`, keeping `validate_product` as the single public entry point for validation.
- Keep **prompt and explanation logic** in `llm_explanations.py` so non-LLM parts remain deterministic.
- Use `app.py` only for wiring, presentation, and user interaction.

For more narrative documentation (including a detailed function reference and engine description), consult `README.md` and `docs/ValidationEngine.md`.
