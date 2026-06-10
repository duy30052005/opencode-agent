import MaterialIcon from './MaterialIcon'

/**
 * WorkflowNode — a single step node in the pipeline header.
 * @param {string}  label   - Node label (e.g. "Requirement")
 * @param {'done'|'error'|'active'|'default'} status
 */
export default function WorkflowNode({ label, status = 'default' }) {
  const statusConfig = {
    done: {
      borderColor: 'border-l-secondary',
      iconColor: 'text-secondary',
      icon: 'check_circle',
      textColor: 'text-on-surface',
      spin: false,
    },
    error: {
      borderColor: 'border-l-error',
      iconColor: 'text-error',
      icon: 'cancel',
      textColor: 'text-on-surface',
      spin: false,
    },
    active: {
      borderColor: 'border-l-primary',
      iconColor: 'text-primary',
      icon: 'sync',
      textColor: 'text-primary',
      spin: true,
    },
    default: {
      borderColor: 'border-l-outline-variant',
      iconColor: 'text-on-surface-variant',
      icon: 'radio_button_unchecked',
      textColor: 'text-on-surface-variant',
      spin: false,
    },
  }

  const cfg = statusConfig[status]

  return (
    <div
      className={`glass-card rounded-lg px-4 py-2 flex items-center gap-3 border-l-4 ${cfg.borderColor} min-w-[160px] ${status === 'active' ? 'active-glow' : ''}`}
    >
      <MaterialIcon
        icon={cfg.icon}
        className={`${cfg.iconColor} text-sm ${cfg.spin ? 'animate-spin' : ''}`}
      />
      <span className={`font-label-caps text-label-caps uppercase ${cfg.textColor} truncate`}>
        {label}
      </span>
    </div>
  )
}
