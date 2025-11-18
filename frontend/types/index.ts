// Input to validation API
export interface ProductInput {
  product_name: string
  category: string
  price: number
  age_flag: 'Yes' | 'No'
}

// Field-level validation result
export interface FieldValidation {
  decision: 'pass' | 'warning' | 'hard_stop'
  message: string
  predicted: string | null
  confidence?: number
}

// Price validation with band info
export interface PriceValidation {
  decision: 'pass' | 'warning' | 'hard_stop'
  message: string
  median: number | null
  lower: number | null
  upper: number | null
}

// Age verification validation
export interface AgeVerificationValidation {
  decision: 'pass' | 'warning' | 'hard_stop'
  message: string
  predicted: 'Yes' | 'No' | null
  confidence?: number
}

// Neighbouring HO product
export interface NeighbourProduct {
  ProductName: string
  Category: string
  PriceGBP: number
  AgeVerificationRequired: string
  similarity: number
}

// Complete validation response from API
export interface ValidationResult {
  category: FieldValidation
  price: PriceValidation
  age_verification: AgeVerificationValidation
  overall: string
  neighbours: NeighbourProduct[]
}

// User's decision on suggestions
export interface FieldChange {
  field: 'category' | 'price' | 'age_flag'
  accepted: boolean
  originalValue: string | number
  suggestedValue: string | number
}

// Submission for storage
export interface Submission {
  id: string
  timestamp: string
  product: ProductInput
  validation: ValidationResult
  accepted_changes: FieldChange[]
  notes?: string
  status: 'pending' | 'approved' | 'denied'
  flagged: boolean
}

// API response for submit
export interface SubmitResponse {
  id: string
  status: 'pending' | 'approved'
  timestamp: string
}

// API response for submissions list
export interface SubmissionsResponse {
  pending: Submission[]
  approved: Submission[]
}
