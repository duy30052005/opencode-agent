/**
 * GlassCard — glassmorphism card wrapper.
 * @param {string}  variant  - 'default' | 'panel' | 'success'
 * @param {string}  className - Extra Tailwind classes
 */
export default function GlassCard({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'glass-card',
    panel: 'glass-panel',
    success: 'glass-card-success',
  }

  return (
    <div className={`${variants[variant]} ${className}`}>
      {children}
    </div>
  )
}
