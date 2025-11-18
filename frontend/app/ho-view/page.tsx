'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { Logo } from '@/components/Logo'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { getSubmissions, approveSubmission, denySubmission } from '@/lib/api'
import { Submission } from '@/types'

export default function HOView() {
  const [submissions, setSubmissions] = useState({ pending: [] as Submission[], approved: [] as Submission[] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actioningId, setActioningId] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    fetchSubmissions()
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchSubmissions, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchSubmissions = async () => {
    try {
      const data = await getSubmissions()
      setSubmissions(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch submissions')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id: string) => {
    setActioningId(id)
    try {
      await approveSubmission(id)
      setSuccessMessage('Submission approved')
      await fetchSubmissions()
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve')
    } finally {
      setActioningId(null)
    }
  }

  const handleDeny = async (id: string) => {
    setActioningId(id)
    try {
      await denySubmission(id)
      setSuccessMessage('Submission denied')
      await fetchSubmissions()
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deny')
    } finally {
      setActioningId(null)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Logo size="sm" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Head Office View</h1>
                <p className="text-sm text-gray-600">Product submission management</p>
              </div>
            </div>
            <Link href="/">
              <Button variant="secondary">Back to Submission</Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
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
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-6 rounded-lg bg-red-50 p-4 border border-red-200"
          >
            <p className="text-red-800 font-medium">{error}</p>
          </motion.div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
              <p className="mt-4 text-gray-600">Loading submissions...</p>
            </div>
          </div>
        ) : (
          <div className="grid gap-8 lg:grid-cols-2">
            {/* Pending Submissions */}
            <div>
              <div className="mb-6 flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-900">Pending</h2>
                <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-amber-100 text-amber-800 font-semibold text-sm">
                  {submissions.pending.length}
                </span>
              </div>

              {submissions.pending.length === 0 ? (
                <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
                  <p className="text-gray-500">No pending submissions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <AnimatePresence>
                    {submissions.pending.map((submission) => (
                      <motion.div
                        key={submission.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="rounded-lg bg-white p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                      >
                        <div className="mb-4">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {submission.product.product_name}
                          </h3>
                          <p className="text-sm text-gray-500 mt-1">
                            Submitted{' '}
                            {new Date(submission.timestamp).toLocaleDateString()}
                          </p>
                        </div>

                        <div className="space-y-2 mb-4 text-sm text-gray-700">
                          <div>
                            <span className="font-medium">Category:</span> {submission.product.category}
                          </div>
                          <div>
                            <span className="font-medium">Price:</span> £{submission.product.price.toFixed(2)}
                          </div>
                          <div>
                            <span className="font-medium">Age Verified:</span>{' '}
                            {submission.product.age_flag}
                          </div>
                        </div>

                        {/* Validation Issues */}
                        <div className="mb-4 space-y-2">
                          {submission.validation.category.decision ===
                            'warning' && (
                            <div className="flex items-start gap-2 text-sm">
                              <Badge status="warning" size="sm" />
                              <span className="text-gray-700">
                                {submission.validation.category.message}
                              </span>
                            </div>
                          )}
                          {submission.validation.price.decision === 'warning' && (
                            <div className="flex items-start gap-2 text-sm">
                              <Badge status="warning" size="sm" />
                              <span className="text-gray-700">
                                {submission.validation.price.message}
                              </span>
                            </div>
                          )}
                          {submission.validation.age_verification.decision ===
                            'warning' && (
                            <div className="flex items-start gap-2 text-sm">
                              <Badge status="warning" size="sm" />
                              <span className="text-gray-700">
                                {
                                  submission.validation.age_verification
                                    .message
                                }
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Notes */}
                        {submission.notes && (
                          <div className="mb-4 rounded-lg bg-blue-50 p-3 border border-blue-200 text-sm text-blue-900">
                            <p className="font-medium mb-1">Store Notes:</p>
                            <p>{submission.notes}</p>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleApprove(submission.id)}
                            disabled={actioningId === submission.id}
                            loading={actioningId === submission.id}
                          >
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => handleDeny(submission.id)}
                            disabled={actioningId === submission.id}
                            loading={actioningId === submission.id}
                          >
                            Deny
                          </Button>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>

            {/* Approved Submissions */}
            <div>
              <div className="mb-6 flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-900">Approved</h2>
                <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-green-100 text-green-800 font-semibold text-sm">
                  {submissions.approved.length}
                </span>
              </div>

              {submissions.approved.length === 0 ? (
                <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
                  <p className="text-gray-500">No approved submissions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <AnimatePresence>
                    {submissions.approved.map((submission) => (
                      <motion.div
                        key={submission.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="rounded-lg bg-white p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                      >
                        <div className="mb-4 flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {submission.product.product_name}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                              {new Date(submission.timestamp).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge status="pass" size="sm" />
                        </div>

                        <div className="space-y-2 text-sm text-gray-700">
                          <div>
                            <span className="font-medium">Category:</span>{' '}
                            {submission.product.category}
                          </div>
                          <div>
                            <span className="font-medium">Price:</span> £
                            {submission.product.price.toFixed(2)}
                          </div>
                          <div>
                            <span className="font-medium">Status:</span>{' '}
                            <span className="inline-block px-2 py-1 rounded bg-green-50 text-green-700 text-xs font-medium">
                              {submission.status === 'approved'
                                ? 'Auto-Approved'
                                : 'Approved'}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
