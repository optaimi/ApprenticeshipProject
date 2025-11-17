# JH Product Validation – Demo

Proof-of-concept tool for validating store-submitted products against a head office (HO) product file.

The demo simulates:

- Stores submitting new products (name, category, price, age check).
- Validation against existing HO data using similarity.
- Rules for category, pricing, and age verification.
- A simple web UI using Streamlit.

---

## 1. Prerequisites

- Python 3.10 or later
- Git (optional, if cloning from a repo)

---

## 2. Installation

Clone or copy the project into a folder, then in a terminal:

```bash
cd product-validation-demo

# Create a virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Or on Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
