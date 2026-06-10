import { useEffect } from 'react'
import { useUIStore } from '../../store/useUIStore'
import MaterialIcon from './MaterialIcon'
import { AnimatePresence, motion } from 'framer-motion'

export default function Toast() {
  const { toasts, removeToast } = useUIStore()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => {
          const isError = toast.type === 'error'
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
              className={`glass-card px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 border-l-4 ${
                isError ? 'border-l-error' : 'border-l-secondary'
              }`}
            >
              <MaterialIcon 
                icon={isError ? 'error' : 'info'} 
                className={isError ? 'text-error' : 'text-secondary'}
                size={20}
              />
              <span className="font-body-sm text-body-sm text-on-surface">
                {toast.message}
              </span>
              <button 
                onClick={() => removeToast(toast.id)}
                className="ml-2 text-on-surface-variant hover:text-on-surface"
              >
                <MaterialIcon icon="close" size={16} />
              </button>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
