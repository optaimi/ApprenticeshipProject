import streamlit as st
from validation_engine import df, validate_product

st.set_page_config(page_title="JH Product Validation – Demo", layout="centered")

st.title("JH Product Validation – Demo")
st.write("Submit a new product and see how it compares to HO data.")

with st.form("product_form"):
    product_name = st.text_input("Product name")
    category = st.selectbox("Product category", sorted(df["Category"].unique()))
    price = st.number_input("Product price (£)", min_value=0.0, step=0.01)
    age_flag = st.selectbox("Age verification required?", ["Yes", "No"])
    submitted = st.form_submit_button("Validate")

if submitted:
    if not product_name.strip():
        st.error("Product name is required.")
    else:
        result = validate_product(product_name, category, float(price), age_flag)

        st.subheader("Overall status")
        st.info(result["overall"])

        st.subheader("Category check")
        st.write(f"Decision: **{result['category']['decision']}**")
        st.write(result["category"]["message"])
        if result["category"]["predicted"]:
            st.write(
                f"Predicted category: `{result['category']['predicted']}` "
                f"(confidence {result['category']['confidence']:.0%})"
            )

        st.subheader("Price check")
        st.write(f"Decision: **{result['price']['decision']}**")
        st.write(result["price"]["message"])
        if result["price"]["median"] is not None:
            st.write(
                f"Typical HO price ~£{result['price']['median']:.2f} "
                f"(band £{result['price']['lower']:.2f} – £{result['price']['upper']:.2f})"
            )

        st.subheader("Age verification check")
        st.write(f"Decision: **{result['age_verification']['decision']}**")
        st.write(result["age_verification"]["message"])
        if result["age_verification"]["predicted"]:
            st.write(
                f"Typical HO setting: `{result['age_verification']['predicted']}` "
                f"(confidence {result['age_verification']['confidence']:.0%})"
            )

        with st.expander("Show similar HO products"):
            st.dataframe(
                result["neighbours"][[
                    "ProductName",
                    "Category",
                    "PriceGBP",
                    "AgeVerificationRequired",
                    "similarity",
                ]]
            )