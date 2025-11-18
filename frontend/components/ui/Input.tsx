import React from 'react'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    label,
    error,
    helperText,
    className,
    ...props
  }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-900 mb-2">
            {label}
            {props.required && <span className="text-red-600 ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          {...props}
          className={`
            w-full px-4 py-2.5 rounded-lg border-2 bg-white
            text-gray-900 placeholder-gray-500
            focus:outline-none transition-colors
            ${error ? 'border-red-500 focus:border-red-600' : 'border-gray-200 focus:border-blue-500'}
            ${props.disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
            ${className || ''}
          `}
        />
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
