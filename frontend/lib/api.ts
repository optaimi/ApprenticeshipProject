import {
  ProductInput,
  ValidationResult,
  SubmitResponse,
  SubmissionsResponse,
  FieldChange,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper for API calls with error handling
async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Unknown API error')
  }
}

// Get list of categories
export async function getCategories(): Promise<string[]> {
  const response = await apiCall<{ categories: string[] }>('/api/categories')
  return response.categories
}

// Validate a product
export async function validateProduct(
  product: ProductInput
): Promise<ValidationResult> {
  return apiCall<ValidationResult>('/api/validate', {
    method: 'POST',
    body: JSON.stringify(product),
  })
}

// Submit a product
export async function submitProduct(
  product: ProductInput,
  validation: ValidationResult,
  acceptedChanges: FieldChange[],
  notes: string | undefined,
  flagged: boolean
): Promise<SubmitResponse> {
  return apiCall<SubmitResponse>('/api/submit', {
    method: 'POST',
    body: JSON.stringify({
      product,
      validation,
      accepted_changes: acceptedChanges,
      notes,
      flagged,
    }),
  })
}

// Get all submissions
export async function getSubmissions(): Promise<SubmissionsResponse> {
  return apiCall<SubmissionsResponse>('/api/submissions')
}

// Approve a submission
export async function approveSubmission(submissionId: string): Promise<void> {
  await apiCall(`/api/submissions/${submissionId}/approve`, {
    method: 'POST',
  })
}

// Deny a submission
export async function denySubmission(
  submissionId: string,
  reason?: string
): Promise<void> {
  await apiCall(`/api/submissions/${submissionId}/deny`, {
    method: 'POST',
    body: reason ? JSON.stringify({ reason }) : undefined,
  })
}

// Health check
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await apiCall<{ status: string }>('/health')
    return response.status === 'ok'
  } catch {
    return false
  }
}
