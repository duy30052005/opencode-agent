import { useWorkflowStore } from '../../store/useWorkflowStore'
import MaterialIcon from '../ui/MaterialIcon'
import { motion, AnimatePresence } from 'framer-motion'

export default function ExecutionTimeline({ isOpen, onClose }) {
  const { timelineLogs } = useWorkflowStore()

  const handleDownload = () => {
    const text = timelineLogs.map(l => `[${l.timestamp}] ${l.type.toUpperCase()}: ${l.message}`).join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `execution_logs_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 50, transition: { duration: 0.2 } }}
          className="absolute right-0 top-0 bottom-0 w-80 glass-panel bg-surface/95 backdrop-blur-2xl border-l border-white/10 shadow-2xl z-40 flex flex-col"
        >
          <div className="p-4 border-b border-white/5 flex items-center justify-between bg-surface-container-high/30">
            <div className="flex items-center gap-2">
              <MaterialIcon icon="timeline" className="text-on-surface-variant" size={20} />
              <h3 className="font-headline-md text-body-base font-bold text-on-surface">Execution Timeline</h3>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={handleDownload}
                className="p-1 hover:bg-white/10 rounded text-on-surface-variant transition-colors"
                title="Download Logs"
              >
                <MaterialIcon icon="download" size={18} />
              </button>
              <button 
                onClick={onClose}
                className="p-1 hover:bg-white/10 rounded text-on-surface-variant transition-colors"
              >
                <MaterialIcon icon="close" size={18} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {timelineLogs.length === 0 ? (
              <div className="text-center text-on-surface-variant/50 font-body-sm mt-10 italic">
                No events recorded yet.
              </div>
            ) : (
              <div className="relative">
                {/* Vertical line connecting nodes */}
                <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/10" />
                
                {timelineLogs.map((log, index) => {
                  let colorClass = 'text-on-surface-variant bg-surface-container-highest'
                  let dotColor = 'bg-outline-variant'
                  
                  if (log.type === 'success') {
                    colorClass = 'text-secondary bg-secondary/10'
                    dotColor = 'bg-secondary'
                  } else if (log.type === 'error') {
                    colorClass = 'text-error bg-error/10'
                    dotColor = 'bg-error'
                  } else if (log.type === 'warning') {
                    colorClass = 'text-tertiary-container bg-tertiary-container/10'
                    dotColor = 'bg-tertiary-container'
                  } else if (log.type === 'info') {
                    colorClass = 'text-primary bg-primary/10'
                    dotColor = 'bg-primary'
                  }

                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      key={log.id} 
                      className="relative pl-8 mb-4 last:mb-0"
                    >
                      <div className={`absolute left-0 top-1.5 w-[22px] h-[22px] rounded-full border-4 border-surface ${dotColor} z-10 flex items-center justify-center shadow-md`} />
                      
                      <div className="flex flex-col gap-1">
                        <span className="font-code-base text-[10px] text-on-surface-variant/70">
                          {log.timestamp}
                        </span>
                        <div className={`px-3 py-2 rounded-lg font-body-sm text-sm border border-white/5 ${colorClass}`}>
                          {log.message}
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
