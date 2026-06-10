import { useNavigate, useLocation } from 'react-router-dom'
import { useUIStore } from '../../store/useUIStore'
import { useSessionStore } from '../../store/useSessionStore'
import MaterialIcon from '../ui/MaterialIcon'

const NAV_ITEMS = [
  { id: 'workspace',  label: 'Workspace', icon: 'terminal',    path: '/workspace' },
  { id: 'history',    label: 'History',   icon: 'history',     path: '/history'   },
  { id: 'analytics',  label: 'Analytics', icon: 'query_stats', path: '/analytics' },
  { id: 'settings',   label: 'Settings',  icon: 'settings',    path: '/settings'  },
]

export default function SideNav({ footer, showRetry = false, retryCount = 2, retryMax = 3 }) {
  const navigate = useNavigate()
  const location = useLocation()
  
  const { isSidebarOpen, closeSidebar } = useUIStore()
  const { sessions, currentSessionId, createSession, setCurrentSession, deleteSession } = useSessionStore()

  const handleNewSession = () => {
    const id = createSession('New Chat Task')
    navigate('/workspace')
    closeSidebar()
  }

  const handleSessionClick = (id) => {
    setCurrentSession(id)
    navigate('/workspace')
    closeSidebar()
  }

  return (
    <>
      {/* Mobile backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <nav className={`
        fixed md:static inset-y-0 left-0 z-50 
        w-sidebar-width h-full bg-surface/95 backdrop-blur-xl border-r border-outline-variant
        flex flex-col transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Header */}
        <div className="p-6 border-b border-white/5 flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-container to-inverse-primary flex items-center justify-center shrink-0">
              <MaterialIcon icon="code" className="text-on-primary font-bold" />
            </div>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-primary tracking-tight">
                OpenCode
              </h1>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Agentic Workspace
              </p>
            </div>
          </div>
          <button className="md:hidden text-on-surface-variant" onClick={closeSidebar}>
            <MaterialIcon icon="close" />
          </button>
        </div>

        <div className="px-6 py-4">
          <button
            onClick={handleNewSession}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-primary text-on-primary font-bold hover:bg-primary-fixed transition-colors shadow-[0_0_15px_rgba(192,193,255,0.2)]"
          >
            <MaterialIcon icon="add" size={20} />
            New Chat
          </button>
        </div>

        {/* Main Nav Links */}
        <div className="px-2 pb-2">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname.startsWith(item.path) || (location.pathname === '/' && item.id === 'workspace')
            return (
              <a
                key={item.id}
                href={item.path}
                onClick={(e) => { e.preventDefault(); navigate(item.path); closeSidebar(); }}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors cursor-pointer mb-1 ${
                  isActive
                    ? 'bg-primary/10 text-primary font-semibold'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-white/5'
                }`}
              >
                <MaterialIcon icon={item.icon} fill={isActive} size={20} />
                <span className="font-body-sm text-body-sm">{item.label}</span>
              </a>
            )
          })}
        </div>

        {/* Recent Sessions List */}
        <div className="flex-1 overflow-y-auto px-4 py-2 border-t border-white/5">
          <div className="font-label-caps text-label-caps text-outline-variant mb-3 px-2">RECENT CHATS</div>
          {sessions.length === 0 ? (
            <div className="text-on-surface-variant/50 font-body-sm text-xs px-2 italic">
              No recent chats
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {sessions.map(s => (
                <div 
                  key={s.id}
                  className={`group flex items-center justify-between px-2 py-2 rounded-lg cursor-pointer transition-colors ${
                    s.id === currentSessionId && location.pathname.includes('/workspace')
                      ? 'bg-surface-container-high text-on-surface'
                      : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
                  }`}
                  onClick={() => handleSessionClick(s.id)}
                >
                  <div className="flex items-center gap-2 truncate">
                    <MaterialIcon icon="chat_bubble" size={16} className="opacity-50" />
                    <span className="font-body-sm text-sm truncate">{s.title}</span>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}
                    className="opacity-0 group-hover:opacity-100 text-error hover:text-error-container p-1 rounded"
                    aria-label="Delete Session"
                  >
                    <MaterialIcon icon="delete" size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {footer}
      </nav>
    </>
  )
}
