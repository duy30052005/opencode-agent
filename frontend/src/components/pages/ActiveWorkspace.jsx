import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import TopBar from '../layout/TopBar'
import MaterialIcon from '../ui/MaterialIcon'
import WorkflowNode from '../ui/WorkflowNode'
import TerminalEmulator from '../editor/TerminalEmulator'
import ExecutionTimeline from '../workflow/ExecutionTimeline'
import LangGraphVis from '../workflow/LangGraphVis'
import { useWorkflowStore } from '../../store/useWorkflowStore'
import { useSessionStore } from '../../store/useSessionStore'
import { useUIStore } from '../../store/useUIStore'

const TAB_LINKS = ['Workflow', 'Editor', 'Terminal', 'Logs']

export default function ActiveWorkspace() {
  const navigate = useNavigate()
  const [isTimelineOpen, setIsTimelineOpen] = useState(false)
  const [isGraphOpen, setIsGraphOpen] = useState(false)
  
  const { 
    nodes, 
    currentCode, 
    setCode, 
    errorAnalysis, 
    isExecuting, 
    retryCount,
    maxRetries,
    runMockExecution,
    resetWorkflow
  } = useWorkflowStore()

  const { currentSessionId, sessions } = useSessionStore()
  const { theme, addToast } = useUIStore()

  const currentSession = sessions.find(s => s.id === currentSessionId)

  // Initialize empty state if needed
  useEffect(() => {
    if (!currentSessionId) {
      // Logic handled by SideNav clicking New Chat, but fallback here
    }
    return () => resetWorkflow() // Cleanup on unmount
  }, [currentSessionId, resetWorkflow])

  const handleCopyCode = () => {
    navigator.clipboard.writeText(currentCode)
    addToast('Code copied to clipboard', 'success')
  }

  return (
    <>
      {/* TopBar */}
      <header className="flex justify-between items-center px-gutter h-16 w-full z-40 bg-surface-container/80 backdrop-blur-md border-b border-white/10 shrink-0">
        <div className="flex items-center gap-6">
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight truncate max-w-[300px]">
            {currentSession?.title || 'New Workspace'}
          </h2>
          
          {errorAnalysis && (
            <div className="flex items-center gap-4 border-l border-outline-variant pl-6 animate-fade-in">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-error animate-pulse" />
                <span className="font-body-sm text-body-sm text-error">Analyzing Error</span>
              </div>
              <span className="font-body-sm text-body-sm text-on-surface-variant bg-surface-container-highest px-2 py-1 rounded">
                Retry {retryCount}/{maxRetries}
              </span>
            </div>
          )}
        </div>

        <nav className="flex items-center gap-6">
          <div className="hidden lg:flex gap-6 mr-4">
            {TAB_LINKS.map((tab) => (
              <a
                key={tab}
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  if (tab === 'Logs') setIsTimelineOpen(true)
                  if (tab === 'Workflow') setIsGraphOpen(true)
                }}
                className={`font-body-sm text-body-sm pb-4 pt-4 transition-all ${
                  tab === 'Editor'
                    ? 'text-primary font-bold border-b-2 border-primary'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {tab}
              </a>
            ))}
          </div>
          
          <div className="flex gap-3">
            <button className="hidden sm:block px-4 py-2 rounded-lg border border-white/10 bg-surface/50 font-body-sm text-body-sm hover:bg-white/5 transition-colors">
              Share
            </button>
            <button
              onClick={runMockExecution}
              disabled={isExecuting}
              className={`px-4 py-2 rounded-lg font-body-sm text-body-sm flex items-center gap-2 transition-colors ${
                isExecuting 
                  ? 'bg-surface-container-high text-on-surface-variant cursor-not-allowed'
                  : 'bg-primary text-on-primary hover:bg-primary-fixed shadow-[0_0_15px_rgba(192,193,255,0.2)]'
              }`}
            >
              {isExecuting ? (
                <>
                  <MaterialIcon icon="sync" size={18} className="animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <MaterialIcon icon="play_arrow" size={18} />
                  Execute
                </>
              )}
            </button>
          </div>
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-hidden flex flex-col p-container-padding gap-6 relative">
        
        {/* Workflow nodes */}
        <div className="w-full relative py-2">
          <div className="workflow-line" />
          <div className="flex justify-between items-center relative z-10 w-full px-8">
            {nodes.map((node) => (
              <WorkflowNode key={node.id} label={node.label} status={node.status} />
            ))}
          </div>
        </div>

        {/* Split view */}
        <div className="flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden">
          
          {/* Editor panel */}
          <div className="flex-[3] glass-card rounded-xl flex flex-col overflow-hidden shadow-lg border border-white/5">
            <div className="px-4 py-2 bg-surface-container-high/50 border-b border-white/5 flex justify-between items-center shrink-0">
              <div className="flex items-center gap-3">
                <span className="font-code-base text-code-base text-on-surface-variant">
                  main.py
                </span>
                <span className="px-2 py-0.5 rounded bg-primary/10 text-primary font-label-caps text-[10px] uppercase border border-primary/20">
                  Python
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={handleCopyCode}
                  className="p-1 hover:bg-white/10 rounded text-on-surface-variant transition-colors"
                  title="Copy Code"
                >
                  <MaterialIcon icon="content_copy" size={16} />
                </button>
              </div>
            </div>
            
            <div className="flex-1 relative">
              <Editor
                height="100%"
                language="python"
                theme={theme === 'dark' ? 'vs-dark' : 'light'}
                value={currentCode}
                onChange={(val) => setCode(val || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: '"JetBrains Mono", monospace',
                  padding: { top: 16 },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  readOnly: isExecuting
                }}
              />
            </div>
          </div>

          {/* Terminal panel */}
          <div className="flex-[2] flex flex-col gap-4 overflow-hidden">
            <TerminalEmulator />
            
            {/* Error analysis card */}
            {errorAnalysis && (
              <div className="glass-card border border-error/30 rounded-xl p-4 shrink-0 flex items-start gap-4 bg-error-container/10 animate-slide-up shadow-lg">
                <MaterialIcon icon="warning" className="text-error text-xl mt-1 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-body-base text-body-base font-bold text-on-surface truncate">
                      {errorAnalysis.title}
                    </h3>
                    <span className="font-label-caps text-label-caps bg-primary/20 text-primary px-2 py-1 rounded shrink-0 ml-2">
                      {errorAnalysis.confidence} CONFIDENCE
                    </span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mb-3 break-words">
                    {errorAnalysis.description}
                  </p>
                  <div className="bg-black/30 rounded p-3 font-code-base text-code-base text-on-surface-variant text-sm border border-white/5 break-words">
                    <span className="text-secondary">Suggestion:</span> {errorAnalysis.suggestion}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Streaming thoughts */}
        <div className="h-6 shrink-0 flex items-center gap-3 font-code-base text-code-base text-primary/80">
          {isExecuting && (
            <div className="animate-pulse flex items-center gap-3">
              <span className="text-[8px]">●</span> Processing execution blocks...
            </div>
          )}
        </div>

        {/* Timeline Panel Overlay */}
        <ExecutionTimeline isOpen={isTimelineOpen} onClose={() => setIsTimelineOpen(false)} />
        
        {/* LangGraph Overlay */}
        <LangGraphVis isOpen={isGraphOpen} onClose={() => setIsGraphOpen(false)} />
      </main>
    </>
  )
}
