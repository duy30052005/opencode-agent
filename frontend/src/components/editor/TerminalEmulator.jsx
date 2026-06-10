import { useEffect, useRef } from 'react'
import DOMPurify from 'dompurify'
import MaterialIcon from '../ui/MaterialIcon'
import { useWorkflowStore } from '../../store/useWorkflowStore'

export default function TerminalEmulator() {
  const { terminalOutput, clearTerminal } = useWorkflowStore()
  const scrollRef = useRef(null)

  // Auto-scroll to bottom on new output
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [terminalOutput])

  // Sanitize and format the output (allow basic HTML for colorization if needed)
  const sanitizedOutput = DOMPurify.sanitize(terminalOutput, { 
    ALLOWED_TAGS: ['span', 'br'], 
    ALLOWED_ATTR: ['class', 'style'] 
  })

  // Format newlines to <br/> if they aren't already HTML
  const formattedOutput = sanitizedOutput.replace(/\n/g, '<br/>')

  return (
    <div className="flex-1 glass-panel bg-black/40 rounded-xl flex flex-col overflow-hidden border border-white/5 shadow-lg">
      <div className="px-4 py-2 bg-surface-container-high/30 border-b border-white/5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <MaterialIcon icon="terminal" className="text-sm text-on-surface-variant" />
          <span className="font-code-base text-code-base text-on-surface-variant">Console</span>
        </div>
        <div className="flex gap-2">
          <button 
            className="p-1 hover:bg-white/10 rounded text-on-surface-variant transition-colors"
            title="Download Logs"
          >
            <MaterialIcon icon="download" size={16} />
          </button>
          <button 
            onClick={clearTerminal}
            className="p-1 hover:bg-white/10 rounded text-on-surface-variant transition-colors"
            title="Clear Terminal"
          >
            <MaterialIcon icon="delete" size={16} />
          </button>
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 p-4 font-code-base text-code-base overflow-y-auto text-on-surface-variant scroll-smooth"
      >
        {terminalOutput.length === 0 ? (
          <div className="text-on-surface-variant/50 italic">Waiting for execution...</div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: formattedOutput }} />
        )}
      </div>
    </div>
  )
}
