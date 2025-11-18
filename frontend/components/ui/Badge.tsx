import React from 'react'

export interface BadgeProps {
  status: 'pass' | 'warning' | 'hard_stop'
  size?: 'sm' | 'md'
}

const statusStyles = {
  pass: {
    bg: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200',
    icon: '✓',
  },
  warning: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    icon: '⚠',
  },
  hard_stop: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    icon: '✕',
  },
}

const sizeStyles = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
}

export function Badge({ status, size = 'md' }: BadgeProps) {
  const style = statusStyles[status]
  const sizeClass = sizeStyles[size]

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${style.bg} ${style.border} ${style.text} ${sizeClass}`}
    >
      <span>{style.icon}</span>
      <span className="capitalize">{status === 'hard_stop' ? 'Error' : status}</span>
    </span>
  )
}
