# Frontend Implementation Plan - Product Validation System

## Overview of Current State

The project currently has:
- **validation_engine.py**: Core Python validation logic using TF-IDF similarity matching against 200 HO products from CSV
- **app.py**: Streamlit-based UI (will be replaced with Next.js)
- **llm_explanations.py**: Optional GPT-4.1 nano integration for AI explanations
- **ho_products_dummy_200.csv**: Reference data with 200 products (ProductName, Category, PriceGBP, AgeVerificationRequired, PackSize)

### Validation Engine Behavior

The `validate_product()` function returns structured results with three decision levels:
- **pass**: Field is valid, no action needed (auto-approve eligible)
- **warning**: Field differs from HO pattern, requires review (creates flag)
- **hard_stop**: Critical error, user must fix before submitting

**Key validation rules:**
- **Category**: Warns if store category differs from predicted HO category with confidence ≥70%
- **Price**: Hard stops if ≤0 or >50% deviation from median; warns if 25-50% deviation
- **Age verification**: Hard stops if policy requires "Yes" but store submits "No"; warns on pattern mismatches

**Overall status logic:**
- Any hard_stop → "Requires correction before submission"
- Any warning → "Submitted with warnings; HO will review"
- All pass → "Ready for automatic approval"

## Requirements Summary

### User Product Submission Page
1. Logo placeholder (top left corner)
2. Header description: "Fill in the below form to add your product to the system"
3. Form container with 4 fields:
   - Product Name (text input)
   - Category (dropdown from HO data)
   - Price (number input, GBP)
   - Age Verification Required (Yes/No radio/toggle)
4. **Real-time validation**: On field blur or form submit, call validation API
5. **Inline validation feedback**: Display suggested changes below each field with:
   - Accept/Reject buttons for each suggestion
   - Visual indicators (color-coded badges)
6. **Submit flow**:
   - If hard_stop exists: Block submission, show error
   - If warnings exist and user rejected suggestions: Show confirmation dialog
   - Dialog: "Due to the high risk of incorrect data, this will need to be passed for review, which may cause a slight delay. Do you wish to continue?"
   - If Yes: Prompt for notes to HO team
   - If No flags or user accepts all: Show success message → redirect after 15-20 seconds message
7. **Success scenarios**:
   - No flags: "Successful, your product will be in your price changes in 15-20 minutes"
   - With flags: Submit to HO View with pending status

### Head Office View Page
1. **Two sections**:
   - **Pending Submissions**: Items flagged for review
   - **Successful Submissions**: Auto-approved or manually approved items
2. **Pending submission cards show**:
   - Product details
   - All validation discrepancies with severity indicators
   - User notes (if provided)
   - Approve and Deny buttons
3. **Successful submission cards show**:
   - Product summary
   - Approval timestamp
   - Status badge

## Technical Stack

### Core Technologies
- **Next.js 14+** (App Router for modern file-based routing)
- **TypeScript** (strict mode for type safety)
- **Tailwind CSS** (utility-first styling)

### Minimal Dependencies
- **react-hook-form**: Form state management and validation
- **framer-motion**: Subtle microanimations (fade, slide, scale)
- **zod**: Runtime schema validation (optional but recommended)

### Backend Integration
- Python backend will be wrapped with FastAPI or Flask to expose REST API
- Next.js API routes will proxy to Python backend (avoids CORS in dev)

## Implementation Tasks

### 1. Project Setup & Dependencies
**Estimated effort:** 30 minutes

**Actions:**
```bash
# Initialize Next.js with TypeScript and Tailwind
npx create-next-app@latest product-validation-frontend --typescript --tailwind --app --no-src-dir

# Install dependencies
npm install react-hook-form framer-motion
npm install -D @types/node
```

**Project structure:**
```
product-validation-frontend/
├── app/
│   ├── page.tsx              # User submission form
│   ├── ho-view/
│   │   └── page.tsx          # HO view page
│   ├── api/                  # Next.js API routes (proxy to Python)
│   │   ├── validate/
│   │   ├── submit/
│   │   └── submissions/
│   ├── layout.tsx            # Root layout with logo
│   └── globals.css           # Tailwind imports
├── components/
│   ├── Logo.tsx
│   ├── ProductForm.tsx
│   ├── ValidationFeedback.tsx
│   ├── SuggestionCard.tsx
│   ├── SubmissionCard.tsx
│   ├── ConfirmationModal.tsx
│   └── ui/                   # Small reusable components
│       ├── Badge.tsx
│       ├── Button.tsx
│       └── Input.tsx
├── lib/
│   ├── api.ts               # API client functions
│   └── utils.ts             # Helper functions
├── types/
│   └── index.ts             # TypeScript interfaces
└── tailwind.config.ts
```

### 2. Python API Bridge Setup
**Estimated effort:** 1 hour

**Create:** `backend/api_server.py`

**Requirements:**
- Expose REST endpoints for Next.js frontend
- Use FastAPI (modern, fast, auto-docs) or Flask (simpler)
- Enable CORS for development

**Endpoints:**
```python
POST /api/validate
  Body: { product_name, category, price, age_flag }
  Returns: ValidationResult from validate_product()

POST /api/submit
  Body: { product_name, category, price, age_flag, accepted_changes, notes?, flagged }
  Returns: { submission_id, status }
  Stores submission in memory/JSON file for demo

GET /api/submissions
  Returns: { pending: [], approved: [] }
  Lists all submissions for HO view

POST /api/submissions/:id/approve
  Approves pending submission

POST /api/submissions/:id/deny
  Body: { reason? }
  Denies pending submission
```

**Implementation notes:**
- Store submissions in a simple list or JSON file for demo purposes
- Track submission state: pending/approved/denied
- Include timestamp for each submission

### 3. TypeScript Types & Interfaces
**Estimated effort:** 30 minutes

**Create:** `types/index.ts`

**Define interfaces matching Python validation_engine.py:**
```typescript
// Input to validation
export interface ProductInput {
  product_name: string;
  category: string;
  price: number;
  age_flag: 'Yes' | 'No';
}

// Field-level validation result
export interface FieldValidation {
  decision: 'pass' | 'warning' | 'hard_stop';
  message: string;
  predicted: string | null;
  confidence: number;
}

// Complete validation response
export interface ValidationResult {
  category: FieldValidation & { predicted: string | null };
  price: FieldValidation & { 
    median: number | null;
    lower: number | null;
    upper: number | null;
  };
  age_verification: FieldValidation & { predicted: 'Yes' | 'No' | null };
  overall: string;
  neighbours: Array<{
    ProductName: string;
    Category: string;
    PriceGBP: number;
    AgeVerificationRequired: string;
    similarity: number;
  }>;
}

// User's decision on suggestions
export interface FieldChange {
  field: 'category' | 'price' | 'age_flag';
  accepted: boolean;
  originalValue: string | number;
  suggestedValue: string | number;
}

// Submission for storage
export interface Submission {
  id: string;
  timestamp: string;
  product: ProductInput;
  validation: ValidationResult;
  changes: FieldChange[];
  notes?: string;
  status: 'pending' | 'approved' | 'denied';
  flagged: boolean;
}
```

### 4. Shared UI Components
**Estimated effort:** 2 hours

**Components to build:**

**Logo.tsx**: Placeholder with subtle branding
```typescript
- Simple box with "JH" text or company initials
- Position: top-left, fixed or in header
- Subtle shadow/border
```

**Badge.tsx**: Status indicator
```typescript
- Props: status ('pass' | 'warning' | 'hard_stop'), size
- Colors: green (pass), amber (warning), red (hard_stop)
- Pill shape with icon (checkmark, alert, x)
```

**Button.tsx**: Animated button
```typescript
- Props: variant (primary, secondary, danger), loading, disabled
- Framer Motion: scale on hover (1.02), subtle press animation
- Loading state with spinner
```

**Input.tsx**: Styled form input
```typescript
- Props: label, error, helperText
- Consistent styling across all fields
- Error state with red border and message
```

**ConfirmationModal.tsx**: Dialog component
```typescript
- Props: isOpen, title, message, onConfirm, onCancel
- Framer Motion: fade backdrop, slide-in modal
- Accessible (focus trap, escape to close)
```

### 5. Product Submission Form Page
**Estimated effort:** 3 hours

**File:** `app/page.tsx`

**Layout:**
```
┌─────────────────────────────────────┐
│ [Logo]                              │
│                                     │
│  Fill in the below form to add     │
│  your product to the system.       │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Product Name *               │  │
│  │ [________________]           │  │
│  │ ✓ Looks good                 │  │ <- Pass feedback
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Category *                   │  │
│  │ [Dropdown ▼]                 │  │
│  │ ⚠ Suggested: Alcohol         │  │ <- Warning with suggestion
│  │ [Accept] [Reject]            │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Price (£) *                  │  │
│  │ [______]                     │  │
│  │ ✗ Price must be > 0          │  │ <- Hard stop
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Age Verification Required *  │  │
│  │ ○ Yes  ● No                  │  │
│  └──────────────────────────────┘  │
│                                     │
│  [Submit Product]                   │
│                                     │
└─────────────────────────────────────┘
```

**Features:**
- react-hook-form for state management
- Real-time validation trigger: onChange for price, onBlur for text fields
- Validation feedback appears below each field with fade-in animation
- Track accepted/rejected suggestions in state
- Disable submit if any hard_stop exists
- Show modal if warnings exist and user hasn't accepted suggestions

### 6. Validation Feedback UI
**Estimated effort:** 2 hours

**Component:** `components/ValidationFeedback.tsx`

**Display logic per field:**
```typescript
If decision === 'pass':
  - Show green checkmark badge
  - Display message briefly or hide

If decision === 'warning':
  - Show amber warning badge
  - Display full message
  - Show SuggestionCard if predicted value differs

If decision === 'hard_stop':
  - Show red error badge
  - Display full message prominently
  - Disable submit button
```

**SuggestionCard.tsx:**
```
┌────────────────────────────────────┐
│ ⚠ Suggested Change                 │
│                                    │
│ Your value:  Confectionery         │
│ Suggested:   Alcohol (85% match)   │
│                                    │
│ Most similar products in HO data   │
│ use this category.                 │
│                                    │
│ [Accept Change] [Keep Mine]        │
└────────────────────────────────────┘
```

**Animations:**
- Fade in when validation completes (200ms)
- Slide in suggestion cards from bottom (300ms)
- Color transition on accept/reject (200ms)

### 7. Submit Flow & Flag Handling
**Estimated effort:** 2 hours

**Submit button logic:**
```typescript
1. Check validation results for each field
2. Count hard_stops and warnings
3. Check if user has rejected any warning-level suggestions

If any hard_stop:
  - Disable submit button
  - Show error message: "Please fix errors before submitting"

If warnings exist AND user rejected suggestions:
  - Show confirmation modal
  - Modal content:
    Title: "Review Required"
    Message: "Due to the high risk of incorrect data, this will 
             need to be passed for review, which may cause a 
             slight delay. Do you wish to continue?"
    [Continue] [Cancel]
  
  If user clicks Continue:
    - Show notes textarea modal
    - Placeholder: "Add notes for Head Office team (optional)"
    - [Submit with Notes] [Cancel]
    - On submit: flagged = true

If no warnings OR all suggestions accepted:
  - Submit directly
  - flagged = false
  - Show success message
```

**Success handling:**
```typescript
If flagged === false:
  - Show success message: "Successful! Your product will be in 
    your price changes in 15-20 minutes."
  - Redirect to HO view after 3 seconds (optional)

If flagged === true:
  - Show info message: "Submitted for review. Head Office will 
    review your submission shortly."
  - Redirect to HO view showing pending section
```

### 8. Head Office View Page
**Estimated effort:** 3 hours

**File:** `app/ho-view/page.tsx`

**Layout:**
```
┌──────────────────────────────────────────────┐
│ [Logo]            Head Office View           │
│                                              │
│ ┌──────────────────┐ ┌──────────────────┐   │
│ │ Pending (3)      │ │ Successful (12)  │   │
│ │                  │ │                  │   │
│ │ ┌──────────────┐ │ │ ┌──────────────┐ │   │
│ │ │ Product A    │ │ │ │ Product X    │ │   │
│ │ │ ⚠ Price warn │ │ │ │ ✓ Approved   │ │   │
│ │ │ ⚠ Category   │ │ │ │ 2 mins ago   │ │   │
│ │ │ Notes: ...   │ │ │ └──────────────┘ │   │
│ │ │              │ │ │                  │   │
│ │ │ [Approve]    │ │ │ ┌──────────────┐ │   │
│ │ │ [Deny]       │ │ │ │ Product Y    │ │   │
│ │ └──────────────┘ │ │ │ ✓ Approved   │ │   │
│ │                  │ │ │ 5 mins ago   │ │   │
│ └──────────────────┘ │ └──────────────┘ │   │
│                      └──────────────────┘   │
└──────────────────────────────────────────────┘
```

**Pending submission card:**
```typescript
Display:
- Product name (bold)
- Category, Price, Age verification
- Validation issues with colored badges
- User notes (if provided)
- Action buttons: Approve (green), Deny (red)

On Approve:
  - Move to successful section
  - Show toast: "Product approved"
  - Fade out animation

On Deny:
  - Optional: Prompt for denial reason
  - Remove from list
  - Show toast: "Product denied"
```

**Successful submission card:**
```typescript
Display:
- Product name
- Key details (category, price)
- Green checkmark badge
- Timestamp (relative: "5 mins ago")
- Simplified view (no action buttons)
```

**Features:**
- Fetch submissions from API on mount
- Auto-refresh every 30 seconds (optional)
- Loading skeletons during fetch
- Empty states for no pending/successful items

### 9. State Management & Routing
**Estimated effort:** 1 hour

**State approach:**
- Use React useState/useReducer for component-level state
- Optional: Create context for shared submission data (if needed)
- No heavy state management library needed (keep it simple)

**Form state:**
```typescript
- formData: ProductInput
- validationResult: ValidationResult | null
- acceptedChanges: FieldChange[]
- isValidating: boolean
- isSubmitting: boolean
```

**Navigation flow:**
```typescript
User Form (/) 
  → Submit (no flags) 
    → Success message 
      → Optional redirect to /ho-view

User Form (/)
  → Submit (with flags + notes)
    → Pending message
      → Redirect to /ho-view?section=pending

HO View (/ho-view)
  → Approve/Deny actions
    → Update state
      → Stay on page with toast notification
```

**Loading states:**
- Validation: Show spinner on fields being validated
- Submit: Disable button, show "Submitting..." text
- HO View: Skeleton cards while fetching

### 10. Styling & Microanimations
**Estimated effort:** 2 hours

**Design system (Tailwind config):**
```javascript
// tailwind.config.ts
colors: {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',  // Main blue
    600: '#2563eb',
    700: '#1d4ed8',
  },
  success: '#10b981',  // Green for pass
  warning: '#f59e0b',  // Amber for warnings
  danger: '#ef4444',   // Red for hard_stop
}

// Subtle shadows
boxShadow: {
  'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
  'medium': '0 4px 12px rgba(0, 0, 0, 0.12)',
}
```

**Typography:**
- Headings: font-semibold, text-xl/2xl
- Body: text-base, text-gray-700
- Labels: text-sm, font-medium, text-gray-900

**Animations (Framer Motion):**
```typescript
// Fade in validation feedback
<motion.div
  initial={{ opacity: 0, y: -10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.2 }}
>

// Suggestion card slide in
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
>

// Button hover
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.15 }}
>

// Modal backdrop
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2 }}
>
```

**Responsive design:**
- Mobile-first approach
- Stack HO View sections vertically on mobile
- Adjust form container width: max-w-xl on desktop, full width on mobile

### 11. API Integration & Error Handling
**Estimated effort:** 1.5 hours

**API client (lib/api.ts):**
```typescript
async function validateProduct(input: ProductInput): Promise<ValidationResult>
async function submitProduct(submission: Submission): Promise<{ id: string }>
async function getSubmissions(): Promise<{ pending: [], approved: [] }>
async function approveSubmission(id: string): Promise<void>
async function denySubmission(id: string, reason?: string): Promise<void>
```

**Next.js API routes (proxy pattern):**
```typescript
// app/api/validate/route.ts
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('http://localhost:8000/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return Response.json(await response.json());
}
```

**Error handling:**
- Wrap API calls in try-catch
- Show user-friendly error messages
- Retry logic for network failures (optional)
- Fallback UI for failed states

**Error messages:**
```typescript
Network error: "Unable to connect. Please check your connection."
Validation timeout: "Validation is taking longer than expected. Please try again."
Server error: "Something went wrong. Please try again."
```

### 12. Testing & Demo Data
**Estimated effort:** 1 hour

**Create test scenarios:**
```typescript
1. Valid product (all pass):
   - Name: "Coca-Cola 2L"
   - Category: "Soft drinks"
   - Price: 1.85
   - Age: No
   Result: Auto-approve

2. Price warning:
   - Name: "Sprite 1L"
   - Category: "Soft drinks"
   - Price: 5.00  (median ~1.50)
   Result: Warning, flag for review

3. Hard stop (age policy):
   - Name: "Budweiser Lager 440ml"
   - Category: "Alcohol"
   - Price: 3.00
   - Age: No  (should be Yes)
   Result: Hard stop, cannot submit

4. Category mismatch:
   - Name: "Gordon's Gin 700ml"
   - Category: "Soft drinks"
   - Price: 15.00
   - Age: Yes
   Result: Warning (category), flag for review
```

**Pre-populate HO View with demo submissions:**
```typescript
Create 2-3 pending submissions with various issues
Create 5-10 successful submissions with timestamps
```

**Manual testing checklist:**
- [ ] Form validation triggers correctly
- [ ] Suggestions appear and can be accepted/rejected
- [ ] Submit flow handles flags properly
- [ ] Notes modal appears when needed
- [ ] Success message displays correctly
- [ ] HO View loads submissions
- [ ] Approve/Deny buttons work
- [ ] Animations are smooth and subtle
- [ ] Responsive on mobile and desktop
- [ ] Error states display properly

## Timeline Estimate

| Task | Estimated Time |
|------|---------------|
| 1. Project Setup | 30 mins |
| 2. Python API Bridge | 1 hour |
| 3. TypeScript Types | 30 mins |
| 4. Shared Components | 2 hours |
| 5. Product Form Page | 3 hours |
| 6. Validation Feedback UI | 2 hours |
| 7. Submit Flow | 2 hours |
| 8. HO View Page | 3 hours |
| 9. State & Routing | 1 hour |
| 10. Styling & Animations | 2 hours |
| 11. API Integration | 1.5 hours |
| 12. Testing & Demo Data | 1 hour |
| **Total** | **~19 hours** |

## Notes & Considerations

### Why Next.js?
- Modern App Router with file-based routing
- Built-in API routes for Python backend proxy
- Excellent TypeScript support
- Great developer experience
- Easy deployment (Vercel, etc.)

### Why minimal dependencies?
- Faster build times
- Smaller bundle size
- Less maintenance burden
- Easier to understand and debug

### Production considerations (out of scope for demo):
- Replace in-memory storage with database (PostgreSQL, MongoDB)
- Add authentication and authorization
- Implement proper error logging (Sentry, etc.)
- Add unit and integration tests (Jest, Playwright)
- Set up CI/CD pipeline
- Add rate limiting and input sanitization
- Implement WebSocket for real-time HO View updates

### Alternative approaches considered:
1. **Heavier state management (Redux, Zustand)**: Overkill for this scope
2. **Component library (MUI, Shadcn)**: Adds bulk, custom components give more control
3. **Flask for API**: FastAPI chosen for auto-docs and async support
4. **Separate frontend deployment**: Monorepo simpler for demo

## Getting Started

Once approved, implementation will proceed in order:

1. Initialize Next.js project and install dependencies
2. Create Python FastAPI wrapper around validation_engine.py
3. Build TypeScript type definitions
4. Implement UI components bottom-up (smallest to largest)
5. Wire up API integration
6. Add styling and animations
7. Test thoroughly with various scenarios
8. Create demo data for presentation

Each step will be committed separately for clear history and easier debugging.
