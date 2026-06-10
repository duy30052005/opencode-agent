import { useState } from 'react'
import MaterialIcon from '../ui/MaterialIcon'
import { motion, AnimatePresence } from 'framer-motion'

export default function PromptDetailModal({ isOpen, onClose, session }) {
  if (!session) return null

  // Since we only store basic mock history currently, we'll format what we have
  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(session, null, 2))
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            {/* Modal */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card bg-surface w-full max-w-4xl max-h-[90vh] rounded-xl shadow-2xl flex flex-col overflow-hidden border border-white/10"
            >
              {/* Header */}
              <div className="p-6 border-b border-white/5 flex items-center justify-between bg-surface-container-low/50">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <MaterialIcon icon="history" className="text-primary" />
                  </div>
                  <div>
                    <h2 className="font-headline-md text-headline-md font-bold text-on-surface">
                      {session.title}
                    </h2>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">
                      Task ID: {session.id.substring(0, 8)} • Language: {session.language}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={handleCopy} className="p-2 hover:bg-white/10 rounded-lg text-on-surface-variant transition-colors" title="Copy Details">
                    <MaterialIcon icon="content_copy" size={20} />
                  </button>
                  <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg text-on-surface-variant transition-colors" title="Close">
                    <MaterialIcon icon="close" size={20} />
                  </button>
                </div>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Status Banner */}
                <div className={`p-4 rounded-lg flex items-center gap-3 border ${
                  session.status === 'success' 
                    ? 'bg-secondary/10 border-secondary/20 text-secondary' 
                    : session.status === 'failed'
                      ? 'bg-error/10 border-error/20 text-error'
                      : 'bg-primary/10 border-primary/20 text-primary'
                }`}>
                  <MaterialIcon 
                    icon={session.status === 'success' ? 'check_circle' : session.status === 'failed' ? 'error' : 'sync'} 
                  />
                  <span className="font-label-caps text-label-caps uppercase tracking-wider">
                    Execution Status: {session.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column */}
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-2">ORIGINAL PROMPT</h3>
                      <div className="p-4 bg-surface-container-highest rounded-lg font-body-sm text-body-sm text-on-surface border border-white/5">
                        {session.title} (Mock prompt text placeholder)
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-2">ERROR ANALYSIS</h3>
                      <div className="p-4 bg-error-container/10 border border-error/20 rounded-lg font-body-sm text-body-sm text-on-surface">
                        {session.status === 'failed' ? 'Recursion depth exceeded during execution.' : 'No errors detected during the final execution pass.'}
                      </div>
                    </div>
                  </div>

                  {/* Right Column */}
                  <div className="space-y-6">
                    <div className="h-full flex flex-col">
                      <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-2 flex justify-between">
                        FINAL CODE
                        <span className="text-primary">{session.language}</span>
                      </h3>
                      <div className="flex-1 p-4 bg-black/40 rounded-lg font-code-base text-code-base text-on-surface border border-white/5 overflow-auto max-h-[300px]">
                        <pre><code>
{`def placeholder_func():
    # Final code snapshot for ${session.title}
    pass`}
                        </code></pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Footer */}
              <div className="p-4 border-t border-white/5 bg-surface-container-low/50 flex justify-end">
                <button onClick={onClose} className="px-6 py-2 rounded-lg bg-surface-container-high hover:bg-surface-variant text-on-surface transition-colors font-body-sm text-body-sm">
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
