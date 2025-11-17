The engine in validation_engine.py:

1. Loads the dummy HO product file (ho_products_dummy_200.csv).
2. Builds a TF–IDF model on ProductName to find similar HO products.
3. For a new submission, finds the most similar HO products and:
    - Category
        - Looks at the most common category among similar items.
        - Compares the store’s category vs the predicted HO category.
        - Returns pass, warning, or hard_stop.
    - Price
        - Calculates a typical HO price (median) from neighbours.
        - Flags outliers using percentage difference thresholds.
    - Age verification
        - Uses HO patterns and simple policy rules (e.g. alcohol keywords).
        - Flags risky mismatches (e.g. alcohol with No age check).
4.Combines these into an overall status:
    - Ready for automatic approval
    - Submitted with warnings; HO will review
    - Requires correction before submission

The Streamlit app in app.py handles the form and displays:
    - Overall status
    - Category, price, and age-check explanations
    - A table of the most similar HO products that drove the decision