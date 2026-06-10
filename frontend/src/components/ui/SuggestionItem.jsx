import MaterialIcon from './MaterialIcon'

/**
 * SuggestionItem — a single suggestion card in the failure state panel.
 * @param {string} icon        - Material icon name
 * @param {string} title       - Suggestion heading
 * @param {string} description - Suggestion detail text
 */
export default function SuggestionItem({ icon, title, description }) {
  return (
    <li className="bg-surface-container-high p-4 rounded-lg border border-white/5 hover:border-white/10 transition-colors cursor-pointer group">
      <div className="flex items-start gap-3">
        <MaterialIcon
          icon={icon}
          size={18}
          className="text-secondary-fixed mt-1"
        />
        <div>
          <h4 className="font-body-base text-body-base font-semibold text-on-surface group-hover:text-primary transition-colors">
            {title}
          </h4>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            {description}
          </p>
        </div>
      </div>
    </li>
  )
}
