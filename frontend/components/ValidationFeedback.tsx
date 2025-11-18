'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { ValidationResult, FieldChange } from '@/types'

export interface ValidationFeedbackProps {
  validation: ValidationResult
  acceptedChanges: FieldChange[]
  onAcceptChange: (field: 'category' | 'price' | 'age_flag') => void
  onRejectChange: (field: 'category' | 'price' | 'age_flag') => void
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: -10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2 },
  },
}

export function ValidationFeedback({
  validation,
  acceptedChanges,
  onAcceptChange,
  onRejectChange,
}: ValidationFeedbackProps) {
  const isFieldAccepted = (field: string) =>
    acceptedChanges.find((c) => c.field === field)?.accepted ?? false

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Category Validation */}
      <motion.div variants={itemVariants} className="rounded-lg border border-gray-200 p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Category</h4>
            <p className="text-sm text-gray-600 mt-1">{validation.category.message}</p>
          </div>
          <Badge status={validation.category.decision} size="sm" />
        </div>
        {validation.category.predicted && (
          <div className="mt-3 text-sm text-gray-700">
            <span className="font-medium">Suggested:</span> {validation.category.predicted}
            {validation.category.confidence !== undefined && (
              <span className="text-gray-500 ml-2">
                ({(validation.category.confidence * 100).toFixed(0)}% match)
              </span>
            )}
          </div>
        )}
        {validation.category.decision === 'warning' &&
          validation.category.predicted &&
          !isFieldAccepted('category') && (
            <div className="mt-4 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onAcceptChange('category')}
              >
                Accept
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onRejectChange('category')}
              >
                Reject
              </Button>
            </div>
          )}
        {isFieldAccepted('category') && (
          <div className="mt-2 text-sm text-green-700">✓ Accepted</div>
        )}
      </motion.div>

      {/* Price Validation */}
      <motion.div variants={itemVariants} className="rounded-lg border border-gray-200 p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Price</h4>
            <p className="text-sm text-gray-600 mt-1">{validation.price.message}</p>
          </div>
          <Badge status={validation.price.decision} size="sm" />
        </div>
        {validation.price.median !== null && (
          <div className="mt-3 text-sm text-gray-700 space-y-1">
            <div>
              <span className="font-medium">Typical HO price:</span> £{validation.price.median.toFixed(2)}
            </div>
            {validation.price.lower !== null && validation.price.upper !== null && (
              <div className="text-gray-500">
                (band: £{validation.price.lower.toFixed(2)} – £{validation.price.upper.toFixed(2)})
              </div>
            )}
          </div>
        )}
        {(validation.price.decision === 'warning' || validation.price.decision === 'hard_stop') &&
          validation.price.median !== null &&
          !isFieldAccepted('price') && (
            <div className="mt-4 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onAcceptChange('price')}
              >
                Accept
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onRejectChange('price')}
              >
                Reject
              </Button>
            </div>
          )}
        {isFieldAccepted('price') && (
          <div className="mt-2 text-sm text-green-700">✓ Accepted</div>
        )}
      </motion.div>

      {/* Age Verification Validation */}
      <motion.div variants={itemVariants} className="rounded-lg border border-gray-200 p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Age Verification</h4>
            <p className="text-sm text-gray-600 mt-1">
              {validation.age_verification.message}
            </p>
          </div>
          <Badge status={validation.age_verification.decision} size="sm" />
        </div>
        {validation.age_verification.predicted && (
          <div className="mt-3 text-sm text-gray-700">
            <span className="font-medium">Typical HO setting:</span>{' '}
            {validation.age_verification.predicted}
            {validation.age_verification.confidence !== undefined && (
              <span className="text-gray-500 ml-2">
                ({(validation.age_verification.confidence * 100).toFixed(0)}% confident)
              </span>
            )}
          </div>
        )}
        {validation.age_verification.decision === 'warning' &&
          validation.age_verification.predicted &&
          !isFieldAccepted('age_flag') && (
            <div className="mt-4 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onAcceptChange('age_flag')}
              >
                Accept
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onRejectChange('age_flag')}
              >
                Reject
              </Button>
            </div>
          )}
        {isFieldAccepted('age_flag') && (
          <div className="mt-2 text-sm text-green-700">✓ Accepted</div>
        )}
      </motion.div>
    </motion.div>
  )
}
