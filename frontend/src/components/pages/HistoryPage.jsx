import { useState } from 'react'
import TopBar from '../layout/TopBar'
import MaterialIcon from '../ui/MaterialIcon'
import HistoryCard from '../ui/HistoryCard'
import PromptDetailModal from '../workflow/PromptDetailModal'
import { useSessionStore } from '../../store/useSessionStore'

export default function HistoryPage() {
  const { sessions } = useSessionStore()
  const [selectedSession, setSelectedSession] = useState(null)
  
  return (
    <>
      <TopBar showTabs={false} />

      {/* Canvas */}
      <main className="flex-1 overflow-y-auto pt-8 px-container-padding pb-container-padding">
          <div className="max-w-6xl mx-auto">
            {/* Header & Filters */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
              <div>
                <h2 className="font-display-lg text-display-lg text-on-surface">History</h2>
                <p className="font-body-base text-body-base text-on-surface-variant mt-2">
                  Review past execution logs, statuses, and performance metrics.
                </p>
              </div>

              <div className="flex items-center gap-3 glass-panel p-1.5 rounded-lg">
                <div className="relative">
                  <select defaultValue="all" className="appearance-none bg-transparent border-none text-body-sm font-body-sm text-on-surface pl-3 pr-8 py-1.5 focus:ring-0 cursor-pointer">
                    <option className="bg-surface" value="all">All Statuses</option>
                    <option className="bg-surface" value="success">Success</option>
                    <option className="bg-surface" value="failed">Failed</option>
                  </select>
                  <MaterialIcon icon="expand_more" size={16} className="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" />
                </div>
                <div className="w-px h-4 bg-white/10" />
                <div className="relative">
                  <select defaultValue="7" className="appearance-none bg-transparent border-none text-body-sm font-body-sm text-on-surface pl-3 pr-8 py-1.5 focus:ring-0 cursor-pointer">
                    <option className="bg-surface" value="7">Last 7 Days</option>
                    <option className="bg-surface" value="30">Last 30 Days</option>
                    <option className="bg-surface" value="all">All Time</option>
                  </select>
                  <MaterialIcon icon="expand_more" size={16} className="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" />
                </div>
                <button className="p-1.5 rounded-md hover:bg-white/10 text-on-surface-variant transition-colors flex items-center justify-center ml-1">
                  <MaterialIcon icon="filter_list" size={18} />
                </button>
              </div>
            </div>

            {/* Grid/List View */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              {sessions.length === 0 ? (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-on-surface-variant">
                  <MaterialIcon icon="history" size={48} className="mb-4 opacity-50" />
                  <p>No execution history found. Run a task to see it here.</p>
                </div>
              ) : (
                sessions.map((session) => {
                  // Fallback values for mock display
                  const execTime = '1.2s'
                  const retries = session.status === 'failed' ? 3 : 1
                  
                  return (
                    <div key={session.id} onClick={() => setSelectedSession(session)}>
                      <HistoryCard 
                        title={session.title}
                        taskId={session.id.substring(0, 8)}
                        status={session.status === 'idle' ? 'running' : session.status}
                        language={session.language || 'Python'}
                        execTime={execTime}
                        retries={retries}
                      />
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </main>
        
        <PromptDetailModal 
          isOpen={!!selectedSession} 
          session={selectedSession} 
          onClose={() => setSelectedSession(null)} 
        />
    </>
  )
}
