# 📄 Production Feature Specification

**Project Phase:** Future State (Production)
**Goal:** Streamline data entry via automation and drive purchasing compliance.

## 1. Enhanced Data Model
The production form will capture granular product details required for full inventory management:
* **Core Identifiers:** EAN (Barcode), PLOF Code (Product Line/Order Form code).
* **Attributes:** Pack Size (e.g., "24x330ml"), Unit Weight.
* **Commercials:** Supplier Name, Supplier Cost (WSP - Wholesale Supply Price).

## 2. The "Scan & Search" Workflow
The system will implement a tiered lookup strategy to minimise manual entry:

1.  **Trigger:** Store Manager scans a product barcode (EAN).
2.  **Internal Search (Priority):** Check internal stock catalogue.
3.  **External Search (Secondary):** If not found internally, query global EAN Database API.
4.  **Fallback:** If not found anywhere, fallback to manual entry.

## 3. Detailed Behaviour Logic

### Scenario A: Product Exists Internally (We Stock It)
* **Action:** Form auto-populates with our official description, pack size, and category.
* **Restriction:** "Supplier" fields are left blank (since the store is sourcing it locally/elsewhere).
* **Cost Validation (The "Value Add"):**
    * The system compares the Store's input WSP against Head Office's WSP.
    * **Logic:** `IF (HO_WSP < Store_WSP) THEN Trigger Alert`
    * **Alert Message:** *"We stock this item centrally at a lower cost (£{HO_WSP}). Please consider ordering from the depot instead of this local supplier."*

### Scenario B: Product Found in External API (New Line)
* **Action:** Form auto-populates generic details (Product Name, Brand, Image, Pack Size) from the EAN database.
* **User Action:** User only needs to fill in the commercial details (Supplier, Cost, PLOF) and confirm the data.
* **Benefit:** Reduces typing errors and speeds up entry by ~70%.

### Scenario C: Unknown Product (New Local Line)
* **Action:** Form remains blank.
* **User Action:** User completes all fields manually.
* **Validation:** The standard validation engine (from the PoC) runs to check for anomalies in Price/Category logic.
