/**
 * MaterialIcon — wraps Material Symbols Outlined span.
 * @param {string}  icon   - Icon name (e.g. "terminal", "add")
 * @param {boolean} fill   - Whether to use filled variant
 * @param {number}  size   - Font size in px (default 24)
 * @param {string}  className - Extra Tailwind classes
 */
export default function MaterialIcon({ icon, fill = false, size, className = '' }) {
  const style = {
    ...(size ? { fontSize: `${size}px` } : {}),
    ...(fill ? { fontVariationSettings: '"FILL" 1' } : {}),
  }

  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={Object.keys(style).length ? style : undefined}
      aria-hidden="true"
    >
      {icon}
    </span>
  )
}
