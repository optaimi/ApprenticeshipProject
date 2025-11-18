import React from 'react'

export interface LogoProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

const sizeStyles = {
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
}

export function Logo({ className = '', size = 'md' }: LogoProps) {
  return (
    <div
      className={`
        inline-flex items-center justify-center rounded-lg bg-blue-600 font-bold text-white
        ${sizeStyles[size]}
        ${className}
      `}
    >
      JH
    </div>
  )
}
