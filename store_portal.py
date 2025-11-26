"""
Store-facing front end for the JH Product Validation demo.

This app:
- Lets a store submit a product (name, category, price, age verification).
- Calls the shared validation engine.
- Shows inline feedback beneath each field with color highlighting.
- Lets the store accept suggestions or keep their own values.
- Stores each submission (original + final values + decisions) in a CSV file
  for the HO review demo.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st

from validation_engine import df as ho_df, validate_product
from llm_explanations import generate_explanation


# Path for storing submissions for the HO demo
SUBMISSIONS_PATH = Path(__file__).parent / "store_submissions.csv"


def get_categories() -> list[str]:
    """Return a sorted list of unique HO categories for the dropdown."""
    categories = (
        ho_df["Category"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    return categories


def init_session_state() -> None:
    """Initialise Streamlit session state keys used in this app."""
    defaults = {
        "validation_result": None,
        "submission": None,
        "final_category": None,
        "final_price": None,
        "final_age_flag": None,
        "override_reason": "",
        "ai_explanation": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_review_warning(field_data: Dict[str, Any]) -> bool:
    """
    Return True if a field decision is 'warning' AND confidence < 0.70.
    This determines whether the warning should trigger HO review.
    """
    decision = field_data.get("decision", "pass")
    if decision != "warning":
        return False
    confidence = field_data.get("confidence")
    if confidence is None:
        return False
    return confidence < 0.70


def requires_ho_review(result: Dict[str, Any]) -> bool:
    """
    Return True if any field has a hard stop or is a review-level warning.
    This determines whether the submission needs human review at HO.
    """
    for field in ("category", "price", "age_verification"):
        field_data = result.get(field, {})
        decision = field_data.get("decision", "pass")
        if decision == "hard_stop":
            return True
        if is_review_warning(field_data):
            return True
    return False


def has_warning(result: Dict[str, Any]) -> bool:
    """Return True if any field-level decision is a warning."""
    return any(
        result[field]["decision"] == "warning"
        for field in ("category", "price", "age_verification")
        if field in result
    )


def has_hard_stop(result: Dict[str, Any]) -> bool:
    """Return True if any field-level decision is a hard stop."""
    return any(
        result[field]["decision"] == "hard_stop"
        for field in ("category", "price", "age_verification")
        if field in result
    )


def save_submission(record: Dict[str, Any]) -> None:
    """Append a submission record to the CSV file used by the HO demo.

    For the purposes of this demo we simply read, append and rewrite.
    """
    new_row = pd.DataFrame([record])

    if SUBMISSIONS_PATH.exists():
        existing = pd.read_csv(SUBMISSIONS_PATH)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(SUBMISSIONS_PATH, index=False)


def extract_store_section(explanation_text: str) -> str:
    """
    Parse the AI explanation markdown and extract only the 'For the store' section.
    Returns the bullet points without the heading.
    """
    if not explanation_text:
        return ""
    
    # Split by headings
    match = re.search(r"### For the store\s*\n(.*?)(?:### For head office|\Z)", 
                      explanation_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return explanation_text  # fallback to full text if parsing fails


def render_inline_feedback(
    field_name: str,
    decision_data: Dict[str, Any],
    current_value: Any,
    suggested_value: Any,
    key_prefix: str,
) -> None:
    """
    Render inline validation feedback beneath a field.
    Shows color-coded background, concise message, and small action buttons.
    Updates st.session_state["final_{key_prefix}"] when buttons are clicked.
    """
    decision = decision_data.get("decision", "pass")
    
    if decision == "pass":
        return  # No feedback needed
    
    # Determine background color
    if decision == "hard_stop":
        bg_color = "#ffcccc"  # light red
        icon = "⚠️"
    elif decision == "warning":
        bg_color = "#fff3cd"  # light yellow
        icon = "⚠️"
    else:
        bg_color = "#e7f3ff"  # light blue
        icon = "ℹ️"
    
    # Build concise message
    if suggested_value is not None and suggested_value != current_value:
        if field_name.lower() == "category":
            message = f"Are you sure? Most similar products are in the **{suggested_value}** category."
        elif field_name.lower() == "price":
            message = f"Are you sure? Typical price for similar products is **£{suggested_value:.2f}**."
        elif field_name.lower() == "age verification":
            message = f"Are you sure? Most similar products require age verification: **{suggested_value}**."
        else:
            message = decision_data.get("message", "Please review this field.")
    else:
        message = decision_data.get("message", "Please review this field.")
    
    # Render feedback container
    st.markdown(
        f"""<div style="background-color: {bg_color}; padding: 0.75rem; 
        border-radius: 0.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.2em;">{icon}</span> {message}
        </div>""",
        unsafe_allow_html=True
    )
    
    # Show action buttons if there's a suggestion
    if suggested_value is not None and suggested_value != current_value:
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button(f"✓ Accept change", key=f"{key_prefix}_accept", use_container_width=True):
                st.session_state[f"final_{key_prefix}"] = suggested_value
                st.rerun()
        with col2:
            if st.button(f"✗ Keep current", key=f"{key_prefix}_keep", use_container_width=True):
                st.session_state[f"final_{key_prefix}"] = current_value
                st.toast(f"Keeping your {field_name.lower()}", icon="ℹ️")


def main() -> None:
    st.set_page_config(
        page_title="Store Product Submission – Validation Demo",
        page_icon="🛒",
        layout="wide",
    )

    init_session_state()

    st.title("Store product submission")
    st.caption(
        "Add new products to your EPOS system. We'll check them against head office data."
    )
    
    st.divider()

    # Create 2:1 column layout
    col_left, col_right = st.columns([2, 1])

    # ========== LEFT COLUMN: Product form and inline feedback ==========
    with col_left:
        with st.container(border=True):
            st.subheader("Product details")
            
            # Get validation result if it exists
            result = st.session_state.get("validation_result")
            submission = st.session_state.get("submission")
            
            # Product name field
            product_name = st.text_input(
                "Product name",
                value=st.session_state.get("temp_product_name", ""),
                help="Use the name the customer would see on shelf labels.",
                key="product_name_input",
            )
            
            # Category field
            category = st.selectbox(
                "Product category",
                options=get_categories(),
                index=st.session_state.get("temp_category_index", 0),
                help="Choose the best fit category for this product.",
                key="category_input",
            )
            
            # Category inline feedback
            if result and submission:
                category_data = result.get("category", {})
                predicted_category = category_data.get("predicted")
                render_inline_feedback(
                    field_name="Category",
                    decision_data=category_data,
                    current_value=st.session_state["final_category"],
                    suggested_value=predicted_category,
                    key_prefix="category",
                )
            
            # Price field
            price = st.number_input(
                "Retail price (£)",
                min_value=0.0,
                value=st.session_state.get("temp_price", 0.0),
                step=0.05,
                format="%.2f",
                help="Enter the standard single-unit selling price.",
                key="price_input",
            )
            
            # Price inline feedback
            if result and submission:
                price_data = result.get("price", {})
                median_price = price_data.get("median")
                render_inline_feedback(
                    field_name="Price",
                    decision_data=price_data,
                    current_value=st.session_state["final_price"],
                    suggested_value=median_price,
                    key_prefix="price",
                )
            
            # Age verification field
            age_flag = st.selectbox(
                "Age verification required?",
                options=["No", "Yes"],
                index=st.session_state.get("temp_age_index", 0),
                help="Select 'Yes' if staff should perform an age check.",
                key="age_input",
            )
            
            # Age verification inline feedback
            if result and submission:
                age_data = result.get("age_verification", {})
                predicted_flag = age_data.get("predicted")
                render_inline_feedback(
                    field_name="Age verification",
                    decision_data=age_data,
                    current_value=st.session_state["final_age_flag"],
                    suggested_value=predicted_flag,
                    key_prefix="age",
                )
            
            # Check product button
            if st.button("Check product", use_container_width=True, type="primary"):
                if not product_name.strip():
                    st.error("Please enter a product name.")
                else:
                    try:
                        result = validate_product(
                            product_name=product_name.strip(),
                            category=str(category),
                            price=float(price),
                            age_flag=str(age_flag),
                        )
                    except Exception as exc:
                        st.error("Something went wrong while validating the product.")
                        st.exception(exc)
                    else:
                        # Store validation result and submission
                        st.session_state["validation_result"] = result
                        st.session_state["submission"] = {
                            "name": product_name.strip(),
                            "category": str(category),
                            "price": float(price),
                            "age_flag": str(age_flag),
                        }
                        st.session_state["final_category"] = category
                        st.session_state["final_price"] = float(price)
                        st.session_state["final_age_flag"] = age_flag
                        st.session_state["override_reason"] = ""
                        
                        # Store temp values to preserve form state
                        st.session_state["temp_product_name"] = product_name.strip()
                        categories_list = get_categories()
                        st.session_state["temp_category_index"] = categories_list.index(category) if category in categories_list else 0
                        st.session_state["temp_price"] = float(price)
                        st.session_state["temp_age_index"] = ["No", "Yes"].index(age_flag) if age_flag in ["No", "Yes"] else 0
                        
                        # Auto-generate AI explanation
                        try:
                            st.session_state["ai_explanation"] = generate_explanation(
                                submission=st.session_state["submission"],
                                result=result,
                            )
                        except Exception:
                            st.session_state["ai_explanation"] = None
                        
                        st.rerun()

    # ========== RIGHT COLUMN: Comments panel ==========
    with col_right:
        st.subheader("Comments")
        
        ai_explanation = st.session_state.get("ai_explanation")
        if ai_explanation:
            store_section = extract_store_section(ai_explanation)
            if store_section:
                st.markdown(store_section)
            else:
                st.caption("No additional comments available.")
        else:
            st.caption("Comments will appear here after validation.")

    # ========== BELOW COLUMNS: Override notes and submission ==========
    result = st.session_state.get("validation_result")
    submission = st.session_state.get("submission")

    if result and submission:
        st.divider()

        # Override notes (only if there are warnings)
        if has_warning(result):
            st.subheader("Override notes (optional)")
            st.session_state["override_reason"] = st.text_area(
                "If you kept your original values after a warning, "
                "add a short note so head office understands why.",
                value=st.session_state["override_reason"],
                key="override_notes",
            )

        # Submission section
        st.subheader("Submit to head office")

        needs_review = requires_ho_review(result)
        if needs_review:
            st.info(
                "⚠️ This product will be flagged for human review at head office "
                "due to warnings or policy requirements."
            )
        else:
            st.success("✓ This product will be automatically approved.")

        if st.button(
            "Submit product to HO",
            use_container_width=True,
            type="primary",
        ):
            category_data = result.get("category", {})
            price_data = result.get("price", {})
            age_data = result.get("age_verification", {})

            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "store_id": "Demo Store 1",
                "product_name": submission["name"],
                "original_category": submission["category"],
                "final_category": st.session_state["final_category"],
                "category_decision": category_data.get("decision"),
                "category_predicted": category_data.get("predicted"),
                "category_confidence": category_data.get("confidence"),
                "category_message": category_data.get("message"),
                "original_price": submission["price"],
                "final_price": st.session_state["final_price"],
                "price_decision": price_data.get("decision"),
                "price_median": price_data.get("median"),
                "price_lower": price_data.get("lower"),
                "price_upper": price_data.get("upper"),
                "price_message": price_data.get("message"),
                "original_age_flag": submission["age_flag"],
                "final_age_flag": st.session_state["final_age_flag"],
                "age_decision": age_data.get("decision"),
                "age_predicted": age_data.get("predicted"),
                "age_confidence": age_data.get("confidence"),
                "age_message": age_data.get("message"),
                "overall_status": result.get("overall"),
                "has_warning": has_warning(result),
                "has_hard_stop": has_hard_stop(result),
                "requires_ho_review": needs_review,
                "override_reason": st.session_state["override_reason"],
            }

            try:
                save_submission(record)
            except Exception as exc:
                st.error("Could not save the submission for head office review.")
                st.exception(exc)
            else:
                st.success(
                    "✓ Product submitted to head office. "
                    "Your decisions and notes have been recorded."
                )
                st.balloons()


if __name__ == "__main__":
    main()
