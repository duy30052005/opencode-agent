/**
 * BarItem — a labelled horizontal bar for the language distribution chart.
 * @param {string} language  - Language name
 * @param {number} percent   - 0-100
 * @param {string} barColor  - Tailwind bg color class
 * @param {string} [glowColor] - Optional box-shadow color string
 */
export default function BarItem({ language, percent, barColor, glowColor }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex justify-between font-code-base text-code-base text-sm">
        <span className="text-on-surface">{language}</span>
        <span className="text-on-surface-variant">{percent}%</span>
      </div>
      <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} rounded-full`}
          style={{
            width: `${percent}%`,
            ...(glowColor ? { boxShadow: `0 0 10px ${glowColor}` } : {}),
          }}
        />
      </div>
    </div>
  )
}
