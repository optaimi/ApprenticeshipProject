# Frontend Implementation Plan - Product Validation System

## Overview

Replace the Streamlit UI (app.py) with a Next.js 14+ frontend. The Python backend (validation_engine.py) and LLM layer (llm_explanations.py) remain unchanged. The validation logic is rule-based with TF-IDF similarity matching over 200 HO products. Three decision levels exist: pass (auto-approve), warning (creates flag for HO review), and hard_stop (user must fix).

A FastAPI wrapper will expose REST endpoints for the Next.js frontend.

## Current State

### Backend
- **Dependencies**: streamlit, pandas, scikit-learn, openai
- **HO Data**: ho_products_dummy_200.csv with columns: ProductName, Category, PriceGBP, AgeVerificationRequired, PackSize. 200 products loaded into pandas DataFrame.
- **Validation Engine**: Core rule-based validation with TF-IDF similarity. Public API: `validate_product(product_name, category, price, age_flag)` returns structured dict with neighbours, field-level decisions (pass/warning/hard_stop), and overall status.
- **LLM Layer**: Optional GPT-4.1-nano explanations via llm_explanations.py. Does not change decisions, only explains them.

### Frontend
- **Current**: Streamlit UI (app.py) - will be replaced
- **Deployment**: Python 3.10+; no Next.js setup yet
- **No**: Production environment; runs locally

### Validation Logic (Preserved)
- **Category**: Compares store category to predicted HO category from similar products; pass or warning
- **Price**: Checks against median of similar products; pass/warning if ≤50% deviation, hard_stop if >50% or ≤0
- **Age Verification**: Policy-based (alcohol keywords) combined with HO pattern matching; hard_stop if policy requires "Yes" but store submitted "No"
- **Overall**: If any hard_stop → "Requires correction"; if any warning → "Flagged for HO review"; else → "Ready for auto-approval"

## Goals

1. Build Next.js 14+ frontend with TypeScript, Tailwind CSS, react-hook-form, framer-motion
2. Create FastAPI wrapper around Python validation engine for REST API
3. User submission page: form with real-time validation, inline feedback, accept/reject suggestions, submit flow with flag handling
4. Head Office view: pending/successful submission cards, approve/deny actions
5. Preserve all validation logic and rules unchanged

## Implementation Phases

### Phase 1: Research & Setup ✅ COMPLETE (4-6 hours)
- [x] Verify Python environment and dependencies
- [x] Create FastAPI wrapper exposing validation endpoints
- [x] Initialize Next.js project with TypeScript, Tailwind, minimal dependencies

**Deliverables**: 
- ✅ FastAPI app running on localhost:8000 with /api/validate, /api/submit, /api/submissions endpoints (api_server.py created)
- ✅ Next.js project with folder structure in place (frontend/ directory with all configs and layout)
- ✅ Updated requirements.txt with fastapi, uvicorn, python-multipart

**Details**:
- api_server.py: Wrapper providing /health, /api/categories, /api/validate, /api/submit, /api/submissions, /api/submissions/{id}/approve, /api/submissions/{id}/deny endpoints
- Submissions stored in-memory with JSON file persistence (submissions.json)
- CORS enabled for localhost:3000 and localhost:8000
- Next.js 14+ initialized with TypeScript strict mode, Tailwind with custom colors, react-hook-form and framer-motion
- Project structure: app/ (pages and layout), components/ (UI components), lib/ (utilities), types/ (TypeScript interfaces)

### Phase 2: Core Components & Types ✅ COMPLETE (3-4 hours)
- [x] Define TypeScript interfaces matching validation_engine.py output
- [x] Build shared UI components (Logo, Badge, Button, Input, ConfirmationModal)
- [x] Create API client functions for frontend-to-backend communication

**Deliverables**: 
- ✅ types/index.ts: ProductInput, FieldValidation, PriceValidation, AgeVerificationValidation, NeighbourProduct, ValidationResult, FieldChange, Submission, SubmitResponse, SubmissionsResponse
- ✅ components/ui/: Badge, Button (with Framer Motion), Input, ConfirmationModal (with AnimatePresence), Logo
- ✅ lib/api.ts: getCategories, validateProduct, submitProduct, getSubmissions, approveSubmission, denySubmission, healthCheck
- All components use Tailwind CSS with design tokens from tailwind.config.ts
- Error handling with user-friendly messages
- API calls configured via NEXT_PUBLIC_API_URL env var (defaults to localhost:8000)

### Phase 3: User Submission Page ✅ COMPLETE (5-6 hours)
- [x] Implement ProductForm with real-time validation on blur/submit
- [x] Build ValidationFeedback component displaying pass/warning/hard_stop with inline suggestions
- [x] Wire up submit flow: check for hard_stops, show confirmation modal for warnings, handle accepted changes

**Deliverables**: 
- ✅ app/page.tsx: Full product submission form with react-hook-form, real-time validation on field blur
- ✅ ValidationFeedback.tsx: Animated feedback for category, price, age verification with accept/reject buttons
- ✅ Submit flow: Hard stops block submission, warnings trigger confirmation modal, notes textarea for HO review
- ✅ API health check on load with graceful offline handling
- Success/error messages with auto-dismiss after 5 seconds

### Phase 4: Head Office View ✅ COMPLETE (3-4 hours)
- [x] Build pending submission cards with validation discrepancies and action buttons
- [x] Build successful submission cards with approval timestamp
- [x] Implement approve/deny actions, loading states, empty state handling

**Deliverables**: 
- ✅ app/ho-view/page.tsx: Two-column layout with pending and approved sections
- ✅ Pending cards: show validation issues, store notes, approve/deny buttons
- ✅ Approved cards: show key details with checkmark badge, relative timestamps
- ✅ Auto-refresh every 10 seconds, animations on card entry/exit
- ✅ Back navigation link to submission form

### Phase 5: Styling, Animations & Polish ✅ IN PROGRESS
- [x] Apply Tailwind design system (colors, shadows, typography)
- [x] Add Framer Motion animations (fade, slide, hover effects)
- [x] Responsive design (mobile-first), test on multiple screen sizes

**Deliverables**: 
- ✅ Completed tailwind.config.ts with custom color palette (primary blue, success green, warning amber, danger red)
- ✅ Framer Motion animations: staggered container animations, fade-in/out for modals, slide animations for cards
- ✅ Mobile-responsive: container-based layouts, grid-cols-1 on mobile / lg:grid-cols-2 on larger screens
- ✅ All components use consistent shadows (soft, medium) and spacing
- Button hover/tap animations with scale transforms
- Form inputs with focus ring styles

### Phase 6: Testing & Documentation ✅ IN PROGRESS
- [ ] Manual testing with demo scenarios (valid product, price warning, hard stop, category mismatch)
- [ ] Pre-populate HO View with demo submissions
- [ ] Verify error handling, success messages, redirects

**Deliverables**: 
- Test scenarios to be documented
- Demo data to be created
- Error handling verified

## Acceptance Criteria

- User can submit product via form and see real-time validation feedback
- Hard-stop errors block submission; warnings show confirmation modal with optional notes
- All validation decisions match validation_engine.py output exactly
- HO View displays pending and successful submissions with correct status
- Approve/deny actions update submission state
- UI is responsive, animations are smooth, no console errors
- Error messages are user-friendly; network failures handled gracefully

## Technical Decisions

- **State Management**: React useState/useReducer for component-level state; optional context if needed
- **Storage**: In-memory or JSON file for demo; production would use database
- **Why FastAPI**: Auto-docs, async support, straightforward integration with existing Python code
- **Why Minimal Deps**: Faster builds, smaller bundle, easier maintenance and debugging
- **Why Next.js**: Modern App Router, built-in API routes for proxying Python backend, excellent TypeScript support

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| OpenAI API calls may fail | Ensure LLM explanation layer gracefully handles errors (already done in current app.py) |
| CORS issues if frontend and backend not properly configured | Configure CORS in FastAPI early; test end-to-end during Phase 1 |
| TF-IDF model loading time on first request | Pre-compute and cache model in FastAPI startup |
| Validation engine behavior changes during implementation | Keep validation_engine.py unchanged; focus changes to API wrapper only |

## Assumptions

- Validation engine behavior will not change during frontend implementation
- Mock data for HO View is sufficient for demo
- No authentication required for demo
- Frontend and backend run on localhost during development

## Estimated Total Effort

~19 hours (including research, implementation, testing, and polish)

## Implementation Status

✅ PHASES 1–4 COMPLETE, PHASES 5–6 IN PROGRESS

### Summary of Completed Work

Backend (api_server.py):
- FastAPI wrapper with CORS middleware
- Endpoints: /health, /api/categories, /api/validate, /api/submit, /api/submissions, /api/submissions/{id}/approve, /api/submissions/{id}/deny
- In-memory storage with JSON file persistence

Frontend Structure:
- Next.js 14+ initialized with TypeScript strict mode
- Tailwind CSS configured with custom design system
- React-hook-form and Framer Motion integrated

Pages & Components:
- User Submission Form (app/page.tsx): form validation, real-time API calls, modals
- HO View Page (app/ho-view/page.tsx): pending/approved sections, approve/deny actions
- ValidationFeedback component: animated field feedback with suggestions
- Shared UI: Logo, Badge, Button, Input, ConfirmationModal

API Integration:
- Type-safe client (lib/api.ts) with getCategories, validateProduct, submitProduct, getSubmissions, approveSubmission, denySubmission, healthCheck
- Comprehensive TypeScript interfaces (types/index.ts)

Design & UX:
- Tailwind theme (colors, shadows, typography)
- Framer Motion animations on modals/cards/buttons
- Mobile-responsive layouts

### Next Steps for Phase 6: Testing & Running

Quick Setup (Windows):
```powershell
.\setup.ps1  # Automated setup script
```

Manual Setup:
1. Create and activate Python venv:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```
2. Install Python deps: `pip install -r requirements.txt`
3. Start FastAPI: `python api_server.py` (http://localhost:8000)
4. In a new terminal, install Node.js deps and run frontend:
   ```bash
   cd frontend && npm install
   npm run dev  # (http://localhost:3000)
   ```
5. Test flows:
   - Submit product at /
   - Review at /ho-view
6. Verify acceptance criteria and error handling

Note: Keep both terminals running — one for backend (with venv active), one for frontend
