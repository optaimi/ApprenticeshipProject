# Product Validation Frontend - Next.js

A modern Next.js 14+ frontend for the Product Validation System built with TypeScript, Tailwind CSS, react-hook-form, and Framer Motion.

## Features

- **User Product Submission Form** (`/`)
  - Real-time validation on field blur
  - Inline feedback with accept/reject suggestions
  - Confirmation modal for submissions with warnings
  - Success/error messages with auto-dismiss
  - API health check on page load

- **Head Office View** (`/ho-view`)
  - Pending submissions section with validation discrepancies
  - Approved submissions section
  - Approve/Deny actions for pending items
  - Auto-refresh every 10 seconds
  - Smooth animations and transitions

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Forms**: react-hook-form with validation
- **Animations**: Framer Motion
- **HTTP Client**: Fetch API with error handling

## Prerequisites

- Node.js 18+ and npm
- Python backend running on `localhost:8000` (see parent README)

## Setup

### 1. Install Dependencies

powershell.exe -ExecutionPolicy Bypass


$env:Path = "$HOME\nodejs;" + $env:Path  

```bash
cd frontend
npm install
```

### 2. Configure Environment

The `.env.local` file is already configured for local development:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Update this if your FastAPI backend runs on a different URL.

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # User product submission form
│   ├── layout.tsx            # Root layout with Logo
│   ├── globals.css           # Global styles and Tailwind imports
│   └── ho-view/
│       └── page.tsx          # Head Office view page
├── components/
│   ├── Logo.tsx              # JH branding logo
│   ├── ValidationFeedback.tsx # Field validation display with suggestions
│   └── ui/
│       ├── Badge.tsx         # Status indicator (pass/warning/error)
│       ├── Button.tsx        # Animated button with variants
│       ├── Input.tsx         # Form input with error states
│       └── ConfirmationModal.tsx # Modal dialog with animations
├── lib/
│   └── api.ts               # API client functions
├── types/
│   └── index.ts             # TypeScript interfaces
├── tailwind.config.ts       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
├── next.config.js           # Next.js configuration
└── postcss.config.js        # PostCSS configuration
```

## Key Components

### ProductForm Page (`app/page.tsx`)

Main entry point for users to submit products. Features:
- Form fields: product name, category, price, age verification
- Real-time validation on blur
- Validation feedback below form
- Accept/reject suggestions for warnings
- Submit button disabled during validation or if hard errors exist
- Confirmation modal for submissions with warnings
- Notes textarea for HO team

### ValidationFeedback (`components/ValidationFeedback.tsx`)

Displays validation results for each field:
- Category: Shows predicted category with confidence if warning
- Price: Shows median and band information
- Age Verification: Shows predicted setting if warning
- Accept/Reject buttons only shown for warnings
- Animated staggered entrance

### HO View Page (`app/ho-view/page.tsx`)

Head Office dashboard for managing submissions:
- Two-column layout: Pending and Approved sections
- Pending cards show validation discrepancies and store notes
- Action buttons to approve or deny submissions
- Auto-refresh every 10 seconds
- Loading skeletons during fetch
- Empty states with helpful messaging

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`. See `lib/api.ts` for all API functions:

- `getCategories()` - Fetch category list
- `validateProduct(input)` - Validate a product
- `submitProduct(...)` - Submit a product
- `getSubmissions()` - Fetch all submissions
- `approveSubmission(id)` - Approve pending submission
- `denySubmission(id, reason)` - Deny pending submission
- `healthCheck()` - Check if API is online

## Styling

The app uses Tailwind CSS with a custom design system:

### Colors
- **Primary**: Blue (`#3b82f6`)
- **Success**: Green (`#10b981`)
- **Warning**: Amber (`#f59e0b`)
- **Danger**: Red (`#ef4444`)

### Custom Classes
- Soft shadow: `shadow-soft`
- Medium shadow: `shadow-medium`
- Smooth focus rings: `focus:ring-2 focus:ring-offset-2`

## Animations

Uses Framer Motion for smooth interactions:
- Modal backdrop and content fade and scale
- Card entrance/exit animations with stagger
- Button hover/tap scale transforms
- Validation feedback fade-in with stagger

## Error Handling

- API timeouts and network errors show user-friendly messages
- Failed API calls don't crash the app
- Offline detection with grace fallback
- Form validation errors inline with clear messaging
- Success/error toast messages auto-dismiss

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

When adding new features:
1. Follow TypeScript strict mode
2. Use Tailwind for styling
3. Add Framer Motion animations where appropriate
4. Keep components in `components/ui` for reusability
5. Update types in `types/index.ts` as needed
6. Test API integration end-to-end

## Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### API connection refused
Ensure FastAPI backend is running on `localhost:8000`:
```bash
# From project root
python api_server.py
```

### Tailwind styles not showing
Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

### TypeScript errors
Run type check:
```bash
npm run type-check
```

## Production Deployment

Build and start:
```bash
npm run build
npm start
```

For deployment to Vercel:
1. Push to GitHub
2. Connect to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

## License

See parent project LICENSE
