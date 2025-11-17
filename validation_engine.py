import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# ---------- Load HO data ----------
# Adjust these column names if your CSV differs
df = pd.read_csv("ho_products_dummy_200.csv")

df["ProductName"] = df["ProductName"].fillna("")
df["Category"] = df["Category"].fillna("Unknown")

# Build simple similarity model over product names
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(df["ProductName"])

# ---------- Nearest-neighbour helpers ----------

def get_neighbours(product_name: str, top_k: int = 15) -> pd.DataFrame:
    """Return the top_k most similar HO products."""
    q_vec = vectorizer.transform([product_name])
    sims = linear_kernel(q_vec, X).flatten()
    idxs = sims.argsort()[::-1][:top_k]
    neighbours = df.iloc[idxs].copy()
    neighbours["similarity"] = sims[idxs]
    return neighbours


def infer_category(neighbours: pd.DataFrame):
    grouped = neighbours.groupby("Category")["similarity"].sum().sort_values(ascending=False)
    if grouped.empty:
        return None, 0.0
    predicted = grouped.index[0]
    confidence = grouped.iloc[0] / grouped.sum()
    return predicted, float(confidence)


def infer_price_band(neighbours: pd.DataFrame):
    prices = neighbours["PriceGBP"].dropna()
    if prices.empty:
        return None, None, None
    median = prices.median()
    # simple band: ±25% around median
    lower = median * 0.75
    upper = median * 1.25
    return float(median), float(lower), float(upper)


def infer_age_flag(neighbours: pd.DataFrame):
    vals = neighbours["AgeVerificationRequired"].dropna().str.strip().str.lower()
    if vals.empty:
        return None, 0.0
    yes_ratio = (vals == "yes").mean()
    predicted = "Yes" if yes_ratio >= 0.5 else "No"
    confidence = abs(yes_ratio - 0.5) * 2  # 0 to 1
    return predicted, float(confidence)


# ---------- Policy / rules ----------

ALCOHOL_WORDS = [
    "beer", "lager", "cider", "wine", "vodka", "rum", "gin",
    "whisky", "whiskey", "brandy", "alcopop"
]


def requires_age_verification_by_policy(product_name: str, category: str) -> bool:
    name_lower = product_name.lower()
    cat_lower = (category or "").lower()
    if "alcohol" in cat_lower:
        return True
    if any(w in name_lower for w in ALCOHOL_WORDS):
        return True
    # extend later with tobacco / lottery etc.
    return False


def classify_category(store_cat: str, predicted_cat: str, confidence: float):
    if not predicted_cat:
        return "pass", "No clear match found in HO data, category accepted."

    if store_cat == predicted_cat:
        return "pass", f"Category matches typical HO category '{predicted_cat}'."

    if confidence >= 0.7:
        return (
            "warning",
            f"Most similar HO products are in category '{predicted_cat}' "
            f"(confidence {confidence:.0%}). Consider updating."
        )

    return (
        "warning",
        f"Category differs from common HO category '{predicted_cat}', "
        "but model confidence is moderate. Submission will be flagged for review."
    )


def classify_price(price: float, median: float, lower: float, upper: float):
    if median is None:
        return "pass", "No price band available; price accepted."

    if price <= 0:
        return "hard_stop", "Price must be greater than zero."

    diff_pct = (price - median) / median if median > 0 else 0

    if abs(diff_pct) <= 0.25:
        return "pass", f"Price is within ±25% of typical HO price (~£{median:.2f})."

    if abs(diff_pct) <= 0.5:
        return (
            "warning",
            f"Price is {diff_pct:.0%} away from typical HO price (~£{median:.2f})."
            " Submission will be flagged for review."
        )

    return (
        "hard_stop",
        f"Price is an extreme outlier ({diff_pct:.0%} from typical ~£{median:.2f}). "
        "Please check and correct before submitting."
    )


def classify_age_flag(
    product_name: str,
    category: str,
    store_flag: str,
    predicted_flag: str,
    confidence: float
):
    store_flag_norm = (store_flag or "").strip().title()
    predicted_flag_norm = (predicted_flag or "").strip().title() if predicted_flag else None

    policy_requires_yes = requires_age_verification_by_policy(product_name, category)

    if policy_requires_yes and store_flag_norm == "No":
        return (
            "hard_stop",
            "Product appears to be age-restricted by policy. "
            "Age verification must be set to 'Yes'."
        )

    if not predicted_flag_norm:
        return "pass", "No clear age-check pattern in HO data; value accepted."

    if store_flag_norm == predicted_flag_norm:
        return (
            "pass",
            f"Age verification setting matches typical HO pattern ('{predicted_flag_norm}')."
        )

    if confidence >= 0.7:
        return (
            "warning",
            f"Most similar HO products use age verification '{predicted_flag_norm}'. "
            "Submission will be flagged for review."
        )

    return (
        "warning",
        "Age verification differs from many similar HO products; "
        "submission will be flagged for review."
    )


# ---------- Main API ----------

def validate_product(
    product_name: str,
    category: str,
    price: float,
    age_flag: str
):
    neighbours = get_neighbours(product_name, top_k=15)

    pred_cat, cat_conf = infer_category(neighbours)
    median_price, lower_price, upper_price = infer_price_band(neighbours)
    pred_age_flag, age_conf = infer_age_flag(neighbours)

    cat_decision, cat_msg = classify_category(category, pred_cat, cat_conf)
    price_decision, price_msg = classify_price(price, median_price, lower_price, upper_price)
    age_decision, age_msg = classify_age_flag(
        product_name, category, age_flag, pred_age_flag, age_conf
    )

    overall_levels = [cat_decision, price_decision, age_decision]
    if "hard_stop" in overall_levels:
        overall = "Requires correction before submission."
    elif "warning" in overall_levels:
        overall = "Submitted with warnings; HO will review."
    else:
        overall = "Ready for automatic approval."

    return {
        "neighbours": neighbours,
        "category": {
            "decision": cat_decision,
            "predicted": pred_cat,
            "confidence": cat_conf,
            "message": cat_msg,
        },
        "price": {
            "decision": price_decision,
            "median": median_price,
            "lower": lower_price,
            "upper": upper_price,
            "message": price_msg,
        },
        "age_verification": {
            "decision": age_decision,
            "predicted": pred_age_flag,
            "confidence": age_conf,
            "message": age_msg,
        },
        "overall": overall,
    }
