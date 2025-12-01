# 🛠️ Development Log & Roadmap

This document tracks known issues, active bugs, and the future implementation plan for the Product Validation System.

> **Note:** This project is currently in the **Proof of Concept (PoC)** phase. Many "bugs" listed below are known limitations of the demo architecture (e.g., local storage vs. database) and are scheduled for resolution in the production build.

---

## 🐛 Bug Log

### 🔴 Critical / High Priority
*Issues that affect data integrity or critical workflows.*

| ID | Component | Issue Description | Fix Strategy |
| :--- | :--- | :--- | :--- |
| **BUG-01** | **HO View** | **Rejection Logic Error:** When rejecting a pending submission, it incorrectly moves to the "Approved" column/list and may tag it as approved. | **Backend:** Update `api_server.py` to correctly categorize `"status": "denied"` and ensure the frontend `get_submissions` fetches them separately. <br> **Frontend:** Create a specific "Rejected" table in `ho-view`. |
| **BUG-02** | **Backend** | **Data Loss Risk:** Submissions are stored in-memory and only saved to JSON occasionally. Server restarts cause data loss. | **Backend:** Migrate from `submissions.json` to a persistent database (SQLite for Beta, PostgreSQL for Live). |
| **BUG-03** | **Store View** | **API Error Handling:** If the validation engine cannot find a match, it displays a generic "Failed to fetch" error. | **Frontend:** Catch 404/500 errors in `api.ts`. Display a user-friendly message: *"No match found in HO database. Please enter details manually for review."* |

### 🟡 Medium Priority / UX
*Issues that affect usability or user experience.*

| ID | Component | Issue Description | Fix Strategy |
| :--- | :--- | :--- | :--- |
| **UX-01** | **HO View** | **No Action Confirmation:** Clicking Approve or Reject happens instantly, leading to accidental clicks. | **Frontend:** Implement `<ConfirmationModal />` (re-using the existing component) before firing the approve/deny API call. |
| **UX-02** | **HO View** | **Insufficient Review Context:** Pending approvals only show one validation error. Managers need a full summary of *all* flags to make a decision. | **Backend/AI:** Integrate `llm_explanations.py`. On flag, generate a natural language summary (e.g., *"Flagged for Price (+50%) and Category mismatch"*) and send it to the dashboard. |
| **UX-03** | **Store View** | **Form State Loss:** Refreshing the page wipes all entered data. | **Frontend:** Implement `localStorage` caching to save form inputs on change and rehydrate them on page reload. |

### 🔒 Security & Logic
*Issues regarding access control and robustness.*

| ID | Component | Issue Description | Fix Strategy |
| :--- | :--- | :--- | :--- |
| **SEC-01** | **All** | **No Authentication:** The HO Dashboard and Submission API are publicly accessible. | **Global:** Implement Authentication (e.g., NextAuth.js or OAuth2). <br> • **Store:** Login to submit. <br> • **HO:** Admin login to approve/deny. |
| **LOG-01** | **Engine** | **CSV Parsing Fragility:** The engine may crash if the source CSV contains symbols (e.g., "£") in numeric columns. | **Backend:** Add data cleaning in `validation_engine.py`: `df['Price'] = df['Price'].replace('[£,]', '', regex=True).astype(float)`. |

---

## 🗺️ Implementation Roadmap

### Phase 1: Stability & Fixes (Immediate)
* [ ] **Fix Rejection Flow:** Ensure rejected items are stored with `status: denied` and displayed in a separate list.
* [ ] **Error Messaging:** Replace "Failed to fetch" with a "Manual Entry" fallback mode.
* [ ] **Safety Rails:** Add "Are you sure?" confirmation modals to the Head Office dashboard.

### Phase 2: Enhanced Features (Beta)
* [ ] **Submission History:** Add a "My Submissions" view for Store Users to track the status of their requests.
* [ ] **AI Summaries:** Connect the LLM module to the HO Dashboard to provide human-readable explanations for every flagged product.
* [ ] **Form Persistence:** Save draft submissions to local storage so users don't lose work.

### Phase 3: Production Hardening (Live)
* [ ] **Authentication:** Implement Role-Based Access Control (RBAC) for Store vs. HO users.
* [ ] **Database Migration:** Move from JSON files to a managed SQL database (PostgreSQL).
* [ ] **Live API Integration:** Replace the static `ho_products_dummy.csv` with real-time calls to the company's internal Product API.
