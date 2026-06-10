import TopBar from '../layout/TopBar'
import MaterialIcon from '../ui/MaterialIcon'
import { useUIStore } from '../../store/useUIStore'

export default function SettingsPage() {
  const { theme, setTheme, settings, updateSettings, addToast } = useUIStore()

  const handleSave = () => {
    addToast('Settings saved successfully', 'success')
  }
  return (
    <>
      <TopBar showTabs={false} />

      {/* Canvas */}
      <main className="flex-1 overflow-y-auto pt-8 px-container-padding pb-container-padding relative">
          <div className="ambient-glow" />

          <div className="max-w-4xl mx-auto">
            <div className="mb-10">
              <h2 className="font-display-lg text-display-lg text-on-surface">Settings</h2>
              <p className="font-body-base text-body-base text-on-surface-variant mt-2">
                Configure your OpenCode Agent environment and behavior.
              </p>
            </div>

            <div className="space-y-8">
              {/* General Settings */}
              <section className="glass-panel rounded-2xl p-8 border border-white/5">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
                  <MaterialIcon icon="tune" className="text-primary" />
                  <h3 className="font-headline-md text-headline-md text-on-surface">General</h3>
                </div>

                <div className="space-y-6">
                  {/* Theme Select */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <label className="font-body-base text-body-base font-semibold block text-on-surface mb-1">
                        Workspace Theme
                      </label>
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        Select your preferred IDE color scheme.
                      </span>
                    </div>
                    <div className="relative min-w-[200px]">
                      <select 
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                        className="w-full appearance-none bg-surface-container-high border border-outline-variant text-on-surface font-body-sm text-body-sm rounded-lg px-4 py-2.5 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary cursor-pointer transition-colors"
                      >
                        <option value="system">System Default</option>
                        <option value="light">Light Mode</option>
                        <option value="dark">Dark Material (Default)</option>
                        <option value="high-contrast">High Contrast</option>
                      </select>
                      <MaterialIcon icon="expand_more" className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" size={20} />
                    </div>
                  </div>

                  {/* Auto-save Toggle */}
                  <div className="flex items-center justify-between gap-4 pt-4 border-t border-white/5">
                    <div>
                      <label className="font-body-base text-body-base font-semibold block text-on-surface mb-1">
                        Auto-Save Sessions
                      </label>
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        Automatically save session history to local storage.
                      </span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="sr-only peer" 
                        checked={settings.autoSave}
                        onChange={(e) => updateSettings({ autoSave: e.target.checked })}
                      />
                      <div className="w-11 h-6 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-on-surface after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary" />
                    </label>
                  </div>
                </div>
              </section>

              {/* Model Configuration */}
              <section className="glass-panel rounded-2xl p-8 border border-white/5">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
                  <MaterialIcon icon="smart_toy" className="text-secondary" />
                  <h3 className="font-headline-md text-headline-md text-on-surface">Model Configuration</h3>
                </div>

                <div className="space-y-6">
                  {/* Primary Model Select */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <label className="font-body-base text-body-base font-semibold block text-on-surface mb-1">
                        Primary Reasoning Model
                      </label>
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        The core AI model used for code generation and analysis.
                      </span>
                    </div>
                    <div className="relative min-w-[240px]">
                      <select 
                        value={settings.model}
                        onChange={(e) => updateSettings({ model: e.target.value })}
                        className="w-full appearance-none bg-surface-container-high border border-outline-variant text-on-surface font-body-sm text-body-sm rounded-lg px-4 py-2.5 focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary cursor-pointer transition-colors"
                      >
                        <option value="gpt4">GPT-4 Turbo (Recommended)</option>
                        <option value="claude3">Claude 3 Opus</option>
                        <option value="gemini">Gemini 1.5 Pro</option>
                        <option value="llama3">Llama 3 70B (Local)</option>
                      </select>
                      <MaterialIcon icon="expand_more" className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" size={20} />
                    </div>
                  </div>

                  {/* Temperature Slider */}
                  <div className="pt-4 border-t border-white/5">
                    <div className="flex justify-between items-end mb-4">
                      <div>
                        <label className="font-body-base text-body-base font-semibold block text-on-surface mb-1">
                          Creativity / Temperature
                        </label>
                        <span className="font-body-sm text-body-sm text-on-surface-variant">
                          Higher values make the output more creative, lower values make it more deterministic.
                        </span>
                      </div>
                      <span className="font-code-base text-code-base text-secondary bg-secondary/10 px-2 py-1 rounded">
                        {settings.temperature}
                      </span>
                    </div>
                    <input 
                      type="range" 
                      min="0" max="1" step="0.1" 
                      value={settings.temperature}
                      onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
                      className="w-full" 
                    />
                    <div className="flex justify-between text-xs font-label-caps text-on-surface-variant mt-2">
                      <span>0.0 (Precise)</span>
                      <span>1.0 (Creative)</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* Execution Limits */}
              <section className="glass-panel rounded-2xl p-8 border border-white/5">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
                  <MaterialIcon icon="speed" className="text-tertiary-container" />
                  <h3 className="font-headline-md text-headline-md text-on-surface">Execution Limits</h3>
                </div>

                <div className="space-y-6">
                  {/* Max Retries Select */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <label className="font-body-base text-body-base font-semibold block text-on-surface mb-1">
                        Maximum Error Retries
                      </label>
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        How many times the agent should attempt to self-correct upon failure.
                      </span>
                    </div>
                    <div className="relative min-w-[120px]">
                      <select 
                        value={settings.maxRetries}
                        onChange={(e) => updateSettings({ maxRetries: parseInt(e.target.value) })}
                        className="w-full appearance-none bg-surface-container-high border border-outline-variant text-on-surface font-body-sm text-body-sm rounded-lg px-4 py-2.5 focus:outline-none focus:border-tertiary-container focus:ring-1 focus:ring-tertiary-container cursor-pointer transition-colors"
                      >
                        <option value="1">1 Try</option>
                        <option value="3">3 Retries</option>
                        <option value="5">5 Retries</option>
                        <option value="10">10 Retries</option>
                      </select>
                      <MaterialIcon icon="expand_more" className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" size={20} />
                    </div>
                  </div>
                </div>
              </section>

              {/* Action Bar */}
              <div className="flex justify-end gap-4 mt-8 pt-6 border-t border-white/5">
                <button className="px-6 py-2.5 rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-white/5 transition-colors border border-transparent">
                  Discard Changes
                </button>
                <button 
                  onClick={handleSave}
                  className="px-6 py-2.5 rounded-lg font-body-sm text-body-sm text-surface-container-lowest bg-primary hover:bg-primary-fixed transition-colors font-semibold shadow-[0_0_15px_rgba(192,193,255,0.2)]"
                >
                  Save Configuration
                </button>
              </div>
            </div>
          </div>
        </main>
    </>
  )
}
