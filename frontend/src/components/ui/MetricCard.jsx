import MaterialIcon from './MaterialIcon'

/**
 * MetricCard — analytics bento metric cell.
 * @param {string}   label       - Metric name
 * @param {string}   value       - Primary value
 * @param {string}   unit        - Unit suffix (e.g. "%", "s", "M")
 * @param {string}   icon        - Material icon name
 * @param {string}   iconColor   - Tailwind text color class for icon
 * @param {string}   barColor    - Tailwind bg color class for progress bar
 * @param {number}   barWidth    - Width 0-100 (percent)
 * @param {string}   [trend]     - e.g. "+12%" or "-0.3s"
 * @param {boolean}  [trendUp]   - true = green arrow up, false = red/orange down
 * @param {string}   [trendColor]- Tailwind text color for trend badge
 * @param {string}   [trendBg]   - Tailwind bg color for trend badge
 * @param {React.ReactNode} [barContent] - Custom bar content override
 */
export default function MetricCard({
  label,
  value,
  unit = '',
  icon,
  iconColor,
  barColor,
  barWidth = 75,
  trend,
  trendUp = true,
  trendColor = 'text-secondary',
  trendBg = 'bg-secondary/10',
  barContent,
}) {
  return (
    <div className="glass-card rounded-xl p-6 relative group overflow-hidden hover:glass-glow transition-all duration-300">
      {/* Background icon */}
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <MaterialIcon icon={icon} className={`text-[64px] ${iconColor}`} />
      </div>

      <p className="font-label-caps text-label-caps uppercase text-on-surface-variant mb-2">
        {label}
      </p>

      <div className="flex items-end gap-3">
        <h3 className="font-display-lg text-[40px] text-on-surface leading-none">
          {value}
          {unit && <span className="text-2xl text-on-surface-variant">{unit}</span>}
        </h3>
        {trend && (
          <span
            className={`font-body-sm text-body-sm ${trendColor} flex items-center mb-1 ${trendBg} px-2 py-0.5 rounded text-xs`}
          >
            <MaterialIcon
              icon={trendUp ? 'arrow_upward' : 'arrow_downward'}
              size={14}
            />
            {trend}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="mt-4 h-1 w-full bg-white/5 rounded-full overflow-hidden">
        {barContent ?? (
          <div
            className={`h-full ${barColor} rounded-full`}
            style={{ width: `${barWidth}%` }}
          />
        )}
      </div>
    </div>
  )
}
