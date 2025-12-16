import * as React from "react"
import { cn } from "../../lib/utils"

export interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info'
  onDismiss?: () => void
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, variant = 'default', onDismiss, ...props }, ref) => {
    // Use assertive for errors/warnings, polite for others
    const ariaLive = variant === 'error' || variant === 'warning' ? 'assertive' : 'polite'
    const role = variant === 'error' || variant === 'warning' ? 'alert' : 'status'
    
    return (
      <div
        ref={ref}
        role={role}
        aria-live={ariaLive}
        aria-atomic="true"
        className={cn(
          "pointer-events-auto fixed bottom-4 right-4 z-50 flex w-full max-w-md items-center justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-lg",
          className
        )}
        onKeyDown={(e) => {
          // Allow dismissing with Escape key
          if (e.key === 'Escape' && onDismiss) {
            onDismiss()
          }
        }}
        tabIndex={0}
        {...props}
      />
    )
  }
)
Toast.displayName = "Toast"

export function Toaster() {
  return (
    <div 
      id="toaster-root" 
      aria-label="Notifications"
      aria-live="polite"
      aria-relevant="additions"
    />
  )
}

export { Toast }
