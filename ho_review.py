# ho_review.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

SUBMISSIONS_PATH = Path("submissions.csv")

STATUS_PENDING: Literal["pending"] = "pending"
STATUS_APPROVED: Literal["approved"] = "approved"
STATUS_REJECTED: Literal["rejected"] = "rejected"

DECISION_SCORE = {
    "hard_stop": 2,
    "warning": 1,
    "pass": 0,
}


def load_submissions() -> pd.DataFrame:
    """
    Load submissions from CSV.

    Ensures required columns exist so the UI does not break
    if the file is missing or has partial data.
    """
    if not SUBMISSIONS_PATH.exists():
        columns = [
            "submission_id",
            "timestamp",
            "store_id",
            "product_name",
            "category",
            "price",
            "age_flag",
            "category_decision",
            "price_decision",
            "age_decision",
            "overall_status",
            "needs_review",
            "status",
            "reviewer_notes",
        ]
        return pd.DataFrame(columns=columns)

    df = pd.read_csv(SUBMISSIONS_PATH)

    # Ensure a stable submission_id
    if "submission_id" not in df.columns:
        df.insert(0, "submission_id", range(1, len(df) + 1))

    # Add any missing columns with sensible defaults
    if "timestamp" not in df.columns:
        df["timestamp"] = None

    if "store_id" not in df.columns:
        df["store_id"] = "Unknown store"

    if "product_name" not in df.columns:
        df["product_name"] = ""

    if "category" not in df.columns:
        df["category"] = ""

    if "price" not in df.columns:
        df["price"] = None

    if "age_flag" not in df.columns:
        df["age_flag"] = ""

    if "category_decision" not in df.columns:
        df["category_decision"] = "pass"

    if "price_decision" not in df.columns:
        df["price_decision"] = "pass"

    if "age_decision" not in df.columns:
        # Name it age_decision in the CSV for clarity
        if "age_verification_decision" in df.columns:
            df["age_decision"] = df["age_verification_decision"]
        else:
            df["age_decision"] = "pass"

    if "overall_status" not in df.columns:
        df["overall_status"] = "Ready for automatic approval"

    if "needs_review" not in df.columns:
        # Anything with a warning or hard stop needs review
        df["needs_review"] = df.apply(
            lambda row: any(
                d in {"warning", "hard_stop"}
                for d in [
                    str(row.get("category_decision", "pass")),
                    str(row.get("price_decision", "pass")),
                    str(row.get("age_decision", "pass")),
                ]
            ),
            axis=1,
        )

    if "status" not in df.columns:
        df["status"] = STATUS_PENDING

    if "reviewer_notes" not in df.columns:
        df["reviewer_notes"] = ""

    # Normalise types a bit
    df["status"] = df["status"].fillna(STATUS_PENDING).str.lower()
    df["needs_review"] = df["needs_review"].fillna(False).astype(bool)

    return df


def save_submissions(df: pd.DataFrame) -> None:
    """Persist the submissions DataFrame back to CSV."""
    df.to_csv(SUBMISSIONS_PATH, index=False)


def compute_risk_score(row: pd.Series) -> int:
    """
    Compute a simple numeric risk score from field decisions.
    Higher score = more HO attention.
    """
    decisions = [
        str(row.get("category_decision", "pass")).lower(),
        str(row.get("price_decision", "pass")).lower(),
        str(row.get("age_decision", "pass")).lower(),
    ]
    score = sum(DECISION_SCORE.get(d, 0) for d in decisions)
    return score


def derive_risk_level(score: int) -> str:
    """Map numeric risk score to a human label."""
    if score >= 3:
        return "High"
    if score >= 1:
        return "Medium"
    return "Low"


def prepare_queue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add risk_score and risk_level columns, and sort by risk then newest first.
    """
    if df.empty:
        return df

    df = df.copy()
    df["risk_score"] = df.apply(compute_risk_score, axis=1)
    df["risk_level"] = df["risk_score"].apply(derive_risk_level)

    # Try to parse timestamp for ordering; fall back to string sort if needed
    if "timestamp" in df.columns:
        try:
            df["_parsed_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            df["_parsed_ts"] = pd.NaT
    else:
        df["_parsed_ts"] = pd.NaT

    df = df.sort_values(
        by=["risk_score", "_parsed_ts"],
        ascending=[False, False],
    )

    return df.drop(columns=["_parsed_ts"])


def render_summary(df: pd.DataFrame) -> None:
    """Show a quick summary of queue volumes and statuses."""
    pending_count = (df["status"] == STATUS_PENDING).sum()
    approved_count = (df["status"] == STATUS_APPROVED).sum()
    rejected_count = (df["status"] == STATUS_REJECTED).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Pending", int(pending_count))
    col2.metric("Approved", int(approved_count))
    col3.metric("Rejected", int(rejected_count))


def main() -> None:
    st.set_page_config(
        page_title="HO Review – Product Validation",
        layout="wide",
    )

    st.title("Head Office Review Queue")
    st.caption(
        "Review store-submitted products, confirm or correct details, "
        "and record approval decisions."
    )

    df = load_submissions()

    if df.empty:
        st.info(
            "No submissions found yet. "
            "Once stores start sending products through the portal, "
            "they will appear here for review."
        )
        return

    df = prepare_queue(df)

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        status_options = ["All", "Pending", "Approved", "Rejected"]
        status_choice = st.selectbox("Status", status_options, index=0)

        risk_levels = ["High", "Medium", "Low"]
        risk_selected = st.multiselect(
            "Risk level",
            options=risk_levels,
            default=risk_levels,
        )

        needs_review_only = st.checkbox(
            "Show items that need review only",
            value=False,
        )

    filtered = df.copy()

    if status_choice != "All":
        status_map = {
            "Pending": STATUS_PENDING,
            "Approved": STATUS_APPROVED,
            "Rejected": STATUS_REJECTED,
        }
        filtered = filtered[filtered["status"] == status_map[status_choice]]

    if risk_selected:
        filtered = filtered[filtered["risk_level"].isin(risk_selected)]

    if needs_review_only:
        filtered = filtered[filtered["needs_review"]]

    if filtered.empty:
        st.warning("No submissions match the current filters.")
        return

    render_summary(df)

    st.subheader("Review queue")

    queue_view = filtered[
        [
            "submission_id",
            "timestamp",
            "store_id",
            "product_name",
            "overall_status",
            "risk_level",
            "status",
        ]
    ].rename(
        columns={
            "submission_id": "ID",
            "timestamp": "Submitted",
            "store_id": "Store",
            "product_name": "Product",
            "overall_status": "Overall",
            "risk_level": "Risk",
            "status": "HO status",
        }
    )

    st.dataframe(
        queue_view,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Submission details")

    for _, row in filtered.iterrows():
        header = f"[{row['submission_id']}] {row['product_name']} – {row['store_id']}"
        with st.expander(header, expanded=False):
            left, right = st.columns([2, 3])

            with left:
                st.markdown("**Store submission**")
                st.text(f"Submission ID: {row['submission_id']}")
                st.text(f"Submitted: {row.get('timestamp', '')}")
                st.text(f"Store: {row.get('store_id', '')}")
                st.text(f"Product name: {row.get('product_name', '')}")
                st.text(f"Category (store): {row.get('category', '')}")
                st.text(f"Price (store): {row.get('price', '')}")
                st.text(f"Age check (store): {row.get('age_flag', '')}")

            with right:
                st.markdown("**Validation decisions**")

                col_a, col_b, col_c = st.columns(3)
                col_a.metric(
                    "Category decision",
                    str(row.get("category_decision", "")).title(),
                )
                col_b.metric(
                    "Price decision",
                    str(row.get("price_decision", "")).title(),
                )
                col_c.metric(
                    "Age decision",
                    str(row.get("age_decision", "")).title(),
                )

                st.text(f"Overall status: {row.get('overall_status', '')}")
                st.text(f"Risk level: {row.get('risk_level', '')}")
                st.text(f"Needs review: {row.get('needs_review', False)}")

                st.markdown("---")
                st.markdown("**HO decision**")

                with st.form(f"review_form_{row['submission_id']}"):
                    # Allow HO to adjust key values if needed
                    new_category = st.text_input(
                        "Corrected category (optional)",
                        value=str(row.get("category", "")),
                        help="Adjust if the store chose the wrong category.",
                    )
                    new_price = st.text_input(
                        "Corrected price (optional)",
                        value=str(row.get("price", "")),
                        help="Adjust if the price needs correcting.",
                    )
                    new_age_flag = st.selectbox(
                        "Corrected age verification flag",
                        options=["", "Yes", "No"],
                        index=["", "Yes", "No"].index(
                            str(row.get("age_flag", "")).title()
                            if str(row.get("age_flag", "")).title()
                            in ["Yes", "No"]
                            else ""
                        ),
                    )

                    status_options_radio = [
                        "Pending",
                        "Approved",
                        "Rejected",
                    ]
                    current_status_label = {
                        STATUS_PENDING: "Pending",
                        STATUS_APPROVED: "Approved",
                        STATUS_REJECTED: "Rejected",
                    }.get(row["status"], "Pending")

                    status_choice_radio = st.radio(
                        "HO status",
                        options=status_options_radio,
                        index=status_options_radio.index(current_status_label),
                        horizontal=True,
                    )

                    reviewer_notes = st.text_area(
                        "Reviewer notes (optional)",
                        value=str(row.get("reviewer_notes", "")),
                        help="Reason for approval, corrections, or rejection.",
                    )

                    submitted = st.form_submit_button("Save decision")

                    if submitted:
                        # Map label back to internal value
                        inverse_status_map = {
                            "Pending": STATUS_PENDING,
                            "Approved": STATUS_APPROVED,
                            "Rejected": STATUS_REJECTED,
                        }
                        new_status_value = inverse_status_map[status_choice_radio]

                        # Reload to avoid clobbering concurrent changes
                        df_latest = load_submissions()

                        mask = df_latest["submission_id"] == row["submission_id"]
                        if not mask.any():
                            st.error(
                                "Could not find this submission in the latest data. "
                                "Try reloading the page."
                            )
                        else:
                            # Update fields
                            df_latest.loc[mask, "category"] = new_category
                            df_latest.loc[mask, "price"] = new_price
                            df_latest.loc[mask, "age_flag"] = new_age_flag
                            df_latest.loc[mask, "status"] = new_status_value
                            df_latest.loc[mask, "reviewer_notes"] = reviewer_notes

                            # Stamp a simple reviewed timestamp if not present
                            if "reviewed_at" not in df_latest.columns:
                                df_latest["reviewed_at"] = None
                            df_latest.loc[
                                mask, "reviewed_at"
                            ] = datetime.utcnow().isoformat()

                            save_submissions(df_latest)
                            st.success("Decision saved.")
                            # Refresh the UI with updated data
                            st.experimental_rerun()


if __name__ == "__main__":
    main()
