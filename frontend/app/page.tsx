'use client'

import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import { Logo } from '@/components/Logo'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { ConfirmationModal } from '@/components/ui/ConfirmationModal'
import { ValidationFeedback } from '@/components/ValidationFeedback'
import {
  getCategories,
  validateProduct,
  submitProduct,
  healthCheck,
} from '@/lib/api'
import { ProductInput, ValidationResult, FieldChange } from '@/types'

interface FormData {
  productName: string
  category: string
  price: string
  ageFlag: 'Yes' | 'No'
}
export default function Home() {
  const [categories, setCategories] = useState<string[]>([])
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [acceptedChanges, setAcceptedChanges] = useState<FieldChange[]>([])
  const [showWarningModal, setShowWarningModal] = useState(false)
  const [showNotesModal, setShowNotesModal] = useState(false)
  const [notes, setNotes] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [apiOnline, setApiOnline] = useState(true)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      productName: '',
      category: '',
      price: '',
      ageFlag: 'No',
    },
  })

  const formValues = watch()
  
  // Load categories and check API health
  useEffect(() => {
    const init = async () => {
      try {
        const isOnline = await healthCheck()
        setApiOnline(isOnline)
        if (isOnline) {
          const cats = await getCategories()
          setCategories(cats)
        }
      } catch {
        setApiOnline(false)
      }
    }
    init()
  }, [])

  // Real-time validation on blur
  const handleFieldBlur = async () => {
    if (!formValues.productName || !formValues.category) return
    if (!formValues.price || isNaN(parseFloat(formValues.price))) return

    setIsValidating(true)
    try {
      const result = await validateProduct({
        product_name: formValues.productName,
        category: formValues.category,
        price: parseFloat(formValues.price),
        age_flag: formValues.ageFlag,
      })
      setValidation(result)
      setErrorMessage('')
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : 'Validation failed'
      )
    } finally {
      setIsValidating(false)
    }
  }

  const handleAcceptChange = (field: 'category' | 'price' | 'age_flag') => {
    // Record the accepted change for audit/HO view
    setAcceptedChanges((prev) => {
      const existing = prev.find((c) => c.field === field)

      const suggestedValue =
        field === 'category'
          ? validation?.category.predicted
          : field === 'age_flag'
            ? validation?.age_verification.predicted
            : validation?.price.median

      const originalValue =
        field === 'category'
          ? formValues.category
          : field === 'price'
            ? parseFloat(formValues.price)
            : formValues.ageFlag

      const change: FieldChange = {
        field,
        accepted: true,
        originalValue,
        suggestedValue: suggestedValue ?? originalValue,
      }

      if (existing) {
        return prev.map((c) => (c.field === field ? { ...c, ...change } : c))
      }

      return [...prev, change]
    })

    // Apply the accepted suggestion directly to the form fields
    if (field === 'category' && validation?.category.predicted) {
      setValue('category', validation.category.predicted, {
        shouldValidate: true,
        shouldDirty: true,
      })
    } else if (field === 'age_flag' && validation?.age_verification.predicted) {
      setValue('ageFlag', validation.age_verification.predicted, {
        shouldValidate: true,
        shouldDirty: true,
      })
    } else if (field === 'price' && validation?.price.median !== null) {
      setValue('price', String(validation.price.median), {
        shouldValidate: true,
        shouldDirty: true,
      })
    }
  }

  const handleRejectChange = (field: 'category' | 'price' | 'age_flag') => {
    setAcceptedChanges((prev) =>
      prev.filter(
        (c) => !(c.field === field && !c.accepted)
      )
    )
  }

  const hasHardStops = validation ? ['category', 'price', 'age_verification'].some(
    (key) =>
      validation[key as keyof ValidationResult]?.decision === 'hard_stop'
  ) : false

  const hasWarnings = validation
    ? ['category', 'price', 'age_verification'].some(
        (key) =>
          validation[key as keyof ValidationResult]?.decision === 'warning'
      )
    : false

  const hasRejectedSuggestions = acceptedChanges.some((c) => !c.accepted)

  const handleFormSubmit = async () => {
    if (!validation) return

    const hasIssues = hasWarnings || hasHardStops

    // If there are any warnings or hard stops, go through the confirmation
    // and notes flow so the submission is flagged for HO review.
    if (hasIssues) {
      setShowWarningModal(true)
      return
    }

    // Submit directly only when there are no issues at all.
    await performSubmit(false)
  }

  const performSubmit = async (flagged: boolean) => {
    if (!validation) return

    setIsSubmitting(true)
    try {
      const response = await submitProduct(
        {
          product_name: formValues.productName,
          category: formValues.category,
          price: parseFloat(formValues.price),
          age_flag: formValues.ageFlag,
        },
        validation,
        acceptedChanges,
        flagged ? notes : undefined,
        flagged
      )

      setShowNotesModal(false)
      setShowWarningModal(false)

      if (response.status === 'approved') {
        setSuccessMessage(
          'Success! Your product will be in your price changes in 15-20 minutes.'
        )
      } else {
        setSuccessMessage(
          'Submitted for review. Head Office will review your submission shortly.'
        )
      }

      reset()
      setValidation(null)
      setAcceptedChanges([])
      setNotes('')

      setTimeout(() => {
        setSuccessMessage('')
      }, 5000)
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : 'Submission failed'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!apiOnline) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-2">
            API Server Offline
          </h1>
          <p className="text-gray-600">
            Please ensure the FastAPI backend is running on localhost:8000
          </p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 py-12">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center gap-3"
        >
          <Logo size="md" />
          <h1 className="text-3xl font-bold text-gray-900">
            Product Validation
          </h1>
        </motion.div>

        {/* Success Message */}
        {successMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-6 rounded-lg bg-green-50 p-4 border border-green-200"
          >
            <p className="text-green-800 font-medium">{successMessage}</p>
          </motion.div>
        )}

        {/* Error Message */}
        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-6 rounded-lg bg-red-50 p-4 border border-red-200"
          >
            <p className="text-red-800 font-medium">{errorMessage}</p>
          </motion.div>
        )}

        {/* Main content: form + validation side panel */}
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)] items-start">
          {/* Form Card */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl bg-white shadow-lg p-8"
          >
            <p className="text-gray-600 mb-6">
              Fill in the below form to add your product to the system
            </p>

            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
              {/* Product Name */}
              <Input
                label="Product Name"
                placeholder="e.g. Coca-Cola 1L"
                {...register('productName', {
                  required: 'Product name is required',
                })}
                error={errors.productName?.message}
                required
                onBlur={handleFieldBlur}
              />

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Category <span className="text-red-600">*</span>
                </label>
                <select
                  {...register('category', {
                    required: 'Category is required',
                  })}
                  onBlur={handleFieldBlur}
                  className={`
                    w-full px-4 py-2.5 rounded-lg border-2 bg-white
                    text-gray-900 font-medium
                    focus:outline-none transition-colors
                    ${(
                      errors.category
                        ? 'border-red-500 focus:border-red-600'
                        : 'border-gray-200 focus:border-blue-500'
                    )}
                  `}
                >
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.category.message}
                  </p>
                )}
              </div>

              {/* Price */}
              <Input
                label="Price (£)"
                type="number"
                placeholder="0.00"
                step="0.01"
                min="0"
                {...register('price', {
                  required: 'Price is required',
                  validate: (val) => {
                    const num = parseFloat(val)
                    return num > 0 || 'Price must be greater than 0'
                  },
                })}
                error={errors.price?.message}
                required
                onBlur={handleFieldBlur}
              />

              {/* Age Verification */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-3">
                  Age Verification Required <span className="text-red-600">*</span>
                </label>
                <div className="flex gap-6">
                  {(['Yes', 'No'] as const).map((option) => (
                    <label
                      key={option}
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <input
                        type="radio"
                        value={option}
                        {...register('ageFlag')}
                        onBlur={handleFieldBlur}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Validation Status */}
              {validation && (
                <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-900">
                        Validation Status
                      </p>
                      <p className="text-sm text-blue-700 mt-1">
                        {validation.overall}
                      </p>
                    </div>
                    <Badge
                      status={
                        hasHardStops ? 'hard_stop' : hasWarnings ? 'warning' : 'pass'
                      }
                    />
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={
                  isValidating ||
                  isSubmitting ||
                  !validation
                }
                loading={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Product'}
              </Button>
            </form>
          </motion.div>

          {/* Validation Feedback */}
          {validation && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="rounded-xl bg-white shadow-lg p-6"
            >
              <ValidationFeedback
                validation={validation}
                acceptedChanges={acceptedChanges}
                onAcceptChange={handleAcceptChange}
                onRejectChange={handleRejectChange}
              />
            </motion.div>
          )}
        </div>
      </div>

      {/* Warning Modal */}
      <ConfirmationModal
        isOpen={showWarningModal}
        title="Review Required"
        message={
          <div className="space-y-2">
            <p>
              Due to the high risk of incorrect data, this will need to be passed
              for review, which may cause a slight delay.
            </p>
            <p>Do you wish to continue?</p>
          </div>
        }
        confirmText="Continue"
        cancelText="Cancel"
        onConfirm={() => setShowNotesModal(true)}
        onCancel={() => setShowWarningModal(false)}
      />

      {/* Notes Modal */}
      <ConfirmationModal
        isOpen={showNotesModal}
        title="Add Notes for Head Office"
        message={
          <div>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any additional notes or context (optional)"
              className="w-full px-3 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-500 focus:outline-none text-sm"
              rows={4}
            />
          </div>
        }
        confirmText="Submit"
        cancelText="Cancel"
        isLoading={isSubmitting}
        onConfirm={() => performSubmit(true)}
        onCancel={() => {
          setShowNotesModal(false)
          setShowWarningModal(true)
        }}
      />
    </main>
  )
}
