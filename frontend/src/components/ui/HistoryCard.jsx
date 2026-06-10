import MaterialIcon from './MaterialIcon'

const STATUS_CONFIG = {
  success: {
    border: 'status-success',
    badge: 'bg-secondary/10 border-secondary/20 text-secondary',
    badgeText: 'SUCCESS',
    icon: 'check_circle',
    iconColor: 'text-secondary',
  },
  failed: {
    border: 'status-failed',
    badge: 'bg-error/10 border-error/20 text-error',
    badgeText: 'FAILED',
    icon: 'error',
    iconColor: 'text-error',
  },
  running: {
    border: 'status-running',
    badge: 'bg-primary/10 border-primary/20 text-primary',
    badgeText: 'RUNNING',
    icon: 'sync',
    iconColor: 'text-primary',
  },
}

const LANG_DOT_COLOR = {
  JavaScript: 'bg-yellow-400',
  Python: 'bg-blue-400',
  TypeScript: 'bg-blue-300',
  Go: 'bg-cyan-400',
  Rust: 'bg-orange-400',
}

/**
 * HistoryCard — session history list item.
 * @param {string}  title     - Task name
 * @param {string}  taskId    - e.g. "#4829A"
 * @param {'success'|'failed'|'running'} status
 * @param {string}  language
 * @param {string}  execTime  - e.g. "45.2s"
 * @param {number}  retries
 */
export default function HistoryCard({ title, taskId, status, language, execTime, retries }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.failed
  const dotColor = LANG_DOT_COLOR[language] ?? 'bg-outline'

  return (
    <div
      className={`glass-card rounded-xl p-5 ${cfg.border} transition-all duration-300 group cursor-pointer relative overflow-hidden`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center border border-white/5">
            <MaterialIcon icon={cfg.icon} className={cfg.iconColor} />
          </div>
          <div>
            <h3 className="font-headline-md text-[18px] font-semibold text-on-surface group-hover:text-primary transition-colors">
              {title}
            </h3>
            <p className="font-code-base text-code-base text-on-surface-variant/70 text-[12px] mt-0.5">
              Task ID: {taskId}
            </p>
          </div>
        </div>
        <span className={`px-2.5 py-1 rounded-full border font-label-caps text-[10px] ${cfg.badge}`}>
          {cfg.badgeText}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div>
          <p className="font-label-caps text-on-surface-variant/60 text-[10px] mb-1">LANGUAGE</p>
          <p className="font-code-base text-code-base text-on-surface flex items-center gap-1.5 text-[13px]">
            <span className={`w-2 h-2 rounded-full ${dotColor}`} />
            {language}
          </p>
        </div>
        <div>
          <p className="font-label-caps text-on-surface-variant/60 text-[10px] mb-1">EXECUTION TIME</p>
          <p className="font-code-base text-code-base text-on-surface text-[13px]">{execTime}</p>
        </div>
        <div>
          <p className="font-label-caps text-on-surface-variant/60 text-[10px] mb-1">RETRIES</p>
          <p className="font-code-base text-code-base text-on-surface text-[13px]">{retries}</p>
        </div>
      </div>

      <div className="absolute right-4 bottom-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <MaterialIcon icon="arrow_forward" className="text-on-surface-variant" />
      </div>
    </div>
  )
}
