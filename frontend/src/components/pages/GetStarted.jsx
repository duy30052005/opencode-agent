import { useNavigate } from 'react-router-dom'
import TopBar from '../layout/TopBar'
import MaterialIcon from '../ui/MaterialIcon'

export default function GetStarted() {
  const navigate = useNavigate()

  return (
    <>
      <TopBar activeTab="Workflow" />

      <main className="flex-1 relative overflow-y-auto overflow-x-hidden flex flex-col items-center justify-center p-container-padding">
          {/* Background layers */}
          <div className="grid-pattern" />
          <div className="animated-bg absolute inset-0 z-0" />

          {/* Content */}
          <div className="z-10 flex flex-col items-center text-center max-w-3xl mx-auto space-y-8 mt-[-10vh]">
            {/* Icon badge */}
            <div className="w-20 h-20 rounded-2xl glass-card flex items-center justify-center mb-4 shadow-[0_0_30px_rgba(73,75,214,0.2)]">
              <MaterialIcon
                icon="code_blocks"
                fill
                className="text-4xl text-primary"
              />
            </div>

            {/* Headline */}
            <div className="space-y-4">
              <h2 className="font-display-lg text-display-lg text-on-surface tracking-tight leading-tight">
                Learn Coding Through <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-inverse-primary">
                  AI Debugging
                </span>
              </h2>
              <p className="font-body-base text-body-base text-on-surface-variant max-w-xl mx-auto">
                Watch an AI Agent write code, run it, debug it, and improve it
                step-by-step. A transparent, interactive way to understand complex
                logic.
              </p>
            </div>

            {/* CTA */}
            <button
              onClick={() => navigate('/workspace')}
              className="glow-button px-8 py-4 rounded-lg font-body-base text-body-base font-semibold text-white flex items-center gap-3 mt-4"
            >
              <MaterialIcon icon="rocket_launch" />
              Start New Task
            </button>

            {/* Keyboard hint */}
            <p className="font-body-sm text-body-sm text-outline-variant mt-8 flex items-center gap-2">
              <MaterialIcon icon="keyboard" size={16} />
              Press
              <kbd className="px-2 py-1 bg-surface-container rounded text-xs mx-1 border border-outline-variant">
                Cmd
              </kbd>
              +
              <kbd className="px-2 py-1 bg-surface-container rounded text-xs mx-1 border border-outline-variant">
                K
              </kbd>
              to open command palette
            </p>
          </div>

          {/* Floating decorative nodes */}
          <div className="absolute top-[20%] left-[10%] glass-card p-4 flex items-center gap-3 opacity-60 pointer-events-none transform -rotate-6">
            <div className="w-2 h-8 bg-secondary rounded-full" />
            <div>
              <div className="font-label-caps text-label-caps text-secondary mb-1">ANALYZING</div>
              <div className="font-code-base text-code-base text-on-surface-variant text-xs">
                src/main.rs
              </div>
            </div>
          </div>

          <div className="absolute bottom-[20%] right-[10%] glass-card p-4 flex items-center gap-3 opacity-60 pointer-events-none transform rotate-3">
            <div className="w-2 h-8 bg-tertiary-container rounded-full" />
            <div>
              <div className="font-label-caps text-label-caps text-tertiary-container mb-1">
                DEBUGGING
              </div>
              <div className="font-code-base text-code-base text-on-surface-variant text-xs">
                Segmentation fault
              </div>
            </div>
          </div>
        </main>
    </>
  )
}
