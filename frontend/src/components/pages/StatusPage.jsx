import TopBar from '../layout/TopBar'
import MaterialIcon from '../ui/MaterialIcon'
import SuggestionItem from '../ui/SuggestionItem'

const SUGGESTIONS = [
  {
    icon: 'edit_note',
    title: 'Simplify the Prompt',
    description: 'Break down the authentication requirement into smaller steps (e.g., just the JWT parsing first).',
  },
  {
    icon: 'library_add',
    title: 'Provide Context',
    description: 'Explicitly mention the required imports (like `import jwt`) in your instructions.',
  },
  {
    icon: 'settings_suggest',
    title: 'Increase Retry Limit',
    description: 'Adjust agent settings to allow more iterations for complex tasks.',
  },
]

export default function StatusPage() {
  return (
    <>
        <TopBar activeTab="" showTabs={false} />

        {/* Failure State Workspace */}
        <div className="flex-1 pt-24 px-container-padding pb-container-padding overflow-y-auto">
          {/* Warning Header Card */}
          <div className="glass-panel error-glow rounded-xl p-8 mb-8 max-w-5xl mx-auto flex flex-col md:flex-row gap-8 items-start relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-tertiary-container" />
            <div className="flex-shrink-0 w-16 h-16 rounded-full bg-error-container/20 border border-error/30 flex items-center justify-center">
              <MaterialIcon icon="error" className="text-error text-[32px]" />
            </div>
            <div className="flex-1">
              <h2 className="font-display-lg text-display-lg text-error mb-2 tracking-tight">
                Agent Task Failed
              </h2>
              <p className="font-body-base text-body-base text-on-surface-variant mb-6 max-w-2xl">
                OpenCode Agent reached the maximum retry limit (5/5) attempting to implement the requested authentication middleware. The generated code consistently failed syntax validation.
              </p>
              <div className="flex flex-wrap gap-4">
                <button className="px-6 py-2 rounded-lg bg-surface-container-high border border-outline-variant text-on-surface font-label-caps text-label-caps hover:bg-surface-variant transition-colors flex items-center gap-2">
                  <MaterialIcon icon="refresh" size={18} />
                  Retry Current Prompt
                </button>
                <button className="px-6 py-2 rounded-lg bg-surface-container-high border border-outline-variant text-on-surface font-label-caps text-label-caps hover:bg-surface-variant transition-colors flex items-center gap-2">
                  <MaterialIcon icon="edit" size={18} />
                  Edit Prompt
                </button>
                <button className="px-6 py-2 rounded-lg bg-surface-container-high border border-outline-variant text-error font-label-caps text-label-caps hover:bg-error-container/20 transition-colors flex items-center gap-2 ml-auto">
                  <MaterialIcon icon="cancel" size={18} />
                  Abort Task
                </button>
              </div>
            </div>
          </div>

          {/* Bento Grid Layout for Details */}
          <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Code Editor View (Left/Main) */}
            <div className="lg:col-span-8 flex flex-col gap-8">
              <div className="glass-card rounded-xl overflow-hidden flex flex-col border border-white/5 shadow-lg">
                <div className="px-4 py-3 bg-surface-container/50 border-b border-white/5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MaterialIcon icon="code" className="text-on-surface-variant" size={18} />
                    <span className="font-label-caps text-label-caps text-on-surface-variant">LATEST GENERATED CODE</span>
                  </div>
                  <span className="text-xs text-error font-code-base bg-error-container/20 px-2 py-1 rounded">auth_middleware.py</span>
                </div>
                <div className="p-4 bg-surface-container-lowest font-code-base text-code-base overflow-x-auto terminal-bg relative">
                  <div className="absolute left-0 top-0 bottom-0 w-12 bg-black/20 border-r border-white/5 text-right pt-4 pr-2 text-white/30 select-none">
                    {Array.from({ length: 11 }, (_, i) => i + 1).map(n => <span key={n}>{n}<br /></span>)}
                  </div>
                  <pre className="pl-10 text-on-surface">
                    <code>
<span className="text-tertiary-container">def</span> <span className="text-primary-fixed">verify_token</span>(req):<br />
{'    '}token = req.headers.get(<span className="text-secondary-fixed">&quot;Authorization&quot;</span>)<br />
{'    '}<span className="text-tertiary-container">if not</span> token:<br />
{'        '}<span className="text-tertiary-container">return</span> <span className="text-error-container">None</span><br />
<br />
{'    '}<span className="text-outline"># Error occurs here due to missing import and malformed JWT call</span><br />
{'    '}<span className="bg-error/20 inline-block w-full border-l-2 border-error pl-2 text-error"><span className="text-tertiary-container">try</span>:<br />
{'        '}decoded = jwt.decode(token, secret_key algorithms=[<span className="text-secondary-fixed">&quot;HS256&quot;</span>])</span><br />
{'        '}<span className="text-tertiary-container">return</span> decoded<br />
{'    '}<span className="text-tertiary-container">except</span> Exception <span className="text-tertiary-container">as</span> e:<br />
{'        '}<span className="text-tertiary-container">raise</span> AuthError(e)
                    </code>
                  </pre>
                </div>
              </div>

              {/* Console View */}
              <div className="glass-card rounded-xl overflow-hidden flex flex-col border border-white/5 shadow-lg">
                <div className="px-4 py-3 bg-surface-container/50 border-b border-white/5 flex items-center gap-2">
                  <MaterialIcon icon="terminal" className="text-error" size={18} />
                  <span className="font-label-caps text-label-caps text-error">LATEST ERROR LOGS</span>
                </div>
                <div className="p-4 bg-[#0a0a0a] font-code-base text-code-base overflow-x-auto min-h-[150px]">
                  <div className="text-on-surface-variant opacity-70 mb-2">&gt;&gt; Running syntax validation...</div>
                  <div className="text-error mb-1">SyntaxError: invalid syntax</div>
                  <div className="text-on-surface-variant">File &quot;/workspace/auth_middleware.py&quot;, line 8</div>
                  <div className="text-on-surface pl-4 mb-1">decoded = jwt.decode(token, secret_key algorithms=[&quot;HS256&quot;])</div>
                  <div className="text-error pl-4 mb-4">^</div>
                  <div className="text-on-surface-variant opacity-70 mb-2">&gt;&gt; Validation failed. Max retries (5) exceeded.</div>
                </div>
              </div>
            </div>

            {/* Suggestions Panel (Right) */}
            <div className="lg:col-span-4">
              <div className="glass-panel rounded-xl p-6 border border-white/10 sticky top-24">
                <div className="flex items-center gap-2 mb-6">
                  <MaterialIcon icon="lightbulb" className="text-primary text-[20px]" />
                  <h3 className="font-headline-md text-headline-md text-on-surface">Suggestions for User</h3>
                </div>
                <ul className="space-y-4">
                  {SUGGESTIONS.map((suggestion, i) => (
                    <SuggestionItem key={i} {...suggestion} />
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
    </>
  )
}
