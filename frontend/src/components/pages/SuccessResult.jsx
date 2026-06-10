import MaterialIcon from '../ui/MaterialIcon'

export default function SuccessResult() {
  return (
    <div className="bg-background text-on-background antialiased h-screen w-screen overflow-hidden flex font-body-base text-body-base">
      {/* Ambient Background Lighting */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-secondary/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px]" />
      </div>

      {/* Main Workspace Area (Simulated Background) */}
      <main className="flex-1 flex flex-col h-full relative z-10 p-gutter md:ml-0 pt-[80px]">
        {/* Workflow Graph Header */}
        <div className="mb-8 relative w-full h-[80px] flex items-center px-container-padding">
          {/* Background connecting line */}
          <div className="node-path w-[80%] left-[10%]" />
          <div className="node-path node-path-success w-[80%] left-[10%] transition-all duration-1000 origin-left scale-x-100" />
          
          <div className="w-full flex justify-between items-center relative z-10">
            {/* Node 1: Analyze */}
            <div className="glass-card flex flex-col items-center p-3 rounded-lg min-w-[120px] border-l-4 border-l-secondary bg-surface-container-low/80 backdrop-blur-md">
              <div className="flex items-center gap-2 mb-1">
                <MaterialIcon icon="check_circle" className="text-secondary" size={18} />
                <span className="font-label-caps text-label-caps text-on-surface uppercase tracking-wider">
                  Analyze
                </span>
              </div>
              <span className="font-body-sm text-body-sm text-on-surface-variant">0.2s</span>
            </div>

            {/* Node 2: Plan */}
            <div className="glass-card flex flex-col items-center p-3 rounded-lg min-w-[120px] border-l-4 border-l-secondary bg-surface-container-low/80 backdrop-blur-md">
              <div className="flex items-center gap-2 mb-1">
                <MaterialIcon icon="check_circle" className="text-secondary" size={18} />
                <span className="font-label-caps text-label-caps text-on-surface uppercase tracking-wider">
                  Plan
                </span>
              </div>
              <span className="font-body-sm text-body-sm text-on-surface-variant">0.1s</span>
            </div>

            {/* Node 3: Execute */}
            <div className="glass-card flex flex-col items-center p-3 rounded-lg min-w-[120px] border-l-4 border-l-secondary bg-surface-container-low/80 backdrop-blur-md">
              <div className="flex items-center gap-2 mb-1">
                <MaterialIcon icon="check_circle" className="text-secondary" size={18} />
                <span className="font-label-caps text-label-caps text-on-surface uppercase tracking-wider">
                  Execute
                </span>
              </div>
              <span className="font-body-sm text-body-sm text-on-surface-variant">0.3s</span>
            </div>

            {/* Node 4: Test (Success Glow) */}
            <div className="glass-card-success flex flex-col items-center p-3 rounded-lg min-w-[140px] border-l-4 border-l-secondary transform scale-110 shadow-[0_0_30px_rgba(78,222,163,0.2)]">
              <div className="flex items-center gap-2 mb-1">
                <MaterialIcon icon="task_alt" className="text-secondary animate-pulse" size={20} />
                <span className="font-label-caps text-label-caps text-secondary font-bold uppercase tracking-wider">
                  Success
                </span>
              </div>
              <span className="font-body-sm text-body-sm text-secondary/80">All Passed</span>
            </div>
          </div>
        </div>

        {/* The Editor / Overlay Container */}
        <div className="flex-1 relative rounded-xl overflow-hidden glass-panel flex flex-col">
          {/* Simulated Editor Background */}
          <div className="absolute inset-0 opacity-30 p-6 terminal-bg">
            <div className="font-code-base text-code-base text-on-surface-variant/50">
              <div className="flex">
                <span className="w-8 text-right mr-4 opacity-30">1</span>
                <span className="syntax-keyword">def</span>{' '}
                <span className="syntax-function">optimize_route</span>(nodes, weights):
              </div>
              <div className="flex">
                <span className="w-8 text-right mr-4 opacity-30">2</span>
                <span className="syntax-comment"># Apply Dijkstra&apos;s algorithm with heuristic</span>
              </div>
              <div className="flex">
                <span className="w-8 text-right mr-4 opacity-30">3</span>{' '}
                distances = {'{'}node: float(<span className="syntax-string">&apos;inf&apos;</span>) <span className="syntax-keyword">for</span> node <span className="syntax-keyword">in</span> nodes{'}'}
              </div>
              <div className="flex">
                <span className="w-8 text-right mr-4 opacity-30">4</span> distances[start_node] = 0
              </div>
              <div className="flex">
                <span className="w-8 text-right mr-4 opacity-30">5</span> <span className="syntax-keyword">return</span> distances
              </div>
            </div>
          </div>

          {/* SUCCESS OVERLAY PANEL */}
          <div className="absolute inset-0 z-20 flex items-center justify-center p-container-padding bg-background/40 backdrop-blur-sm">
            <div className="glass-card-success w-full max-w-3xl rounded-xl flex flex-col overflow-hidden animate-slide-up">
              {/* Header */}
              <div className="p-8 pb-6 text-center border-b border-white/5 relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-32 bg-secondary/20 blur-[60px] rounded-full pointer-events-none" />
                <MaterialIcon
                  icon="check_circle"
                  fill
                  className="text-secondary mb-4 drop-shadow-[0_0_15px_rgba(78,222,163,0.4)]"
                  size={64}
                />
                <h1 className="font-headline-md text-headline-md text-on-surface mb-2 font-bold tracking-tight">
                  Success: Implementation Passed All Tests
                </h1>
                <p className="font-body-base text-body-base text-on-surface-variant">
                  The requested changes have been successfully applied and verified.
                </p>
              </div>

              {/* Metrics Bar */}
              <div className="flex border-b border-white/5 bg-black/20">
                <div className="flex-1 p-4 flex flex-col items-center justify-center border-r border-white/5">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-1">
                    Execution Time
                  </span>
                  <span className="font-code-base text-code-base text-secondary font-medium">0.8s</span>
                </div>
                <div className="flex-1 p-4 flex flex-col items-center justify-center">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-1">
                    Retry Count
                  </span>
                  <span className="font-code-base text-code-base text-on-surface font-medium">2</span>
                </div>
              </div>

              {/* Final Code Snippet */}
              <div className="p-6 bg-surface-container-lowest/80 relative">
                <div className="absolute top-0 left-0 w-1 h-full bg-secondary" />
                <div className="flex justify-between items-center mb-3">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">
                    Final Code Snippet
                  </span>
                </div>
                <pre className="font-code-base text-code-base bg-black/40 p-4 rounded-lg overflow-x-auto border border-white/5">
                  <code className="text-on-surface">
<span className="syntax-keyword">function</span> <span className="syntax-function">resolveDependencyGraph</span>(graph) {'{\n'}
{'  '}<span className="syntax-keyword">const</span> resolved = <span className="syntax-keyword">new</span> <span className="syntax-function">Set</span>();{'\n'}
{'  '}<span className="syntax-keyword">const</span> seen = <span className="syntax-keyword">new</span> <span className="syntax-function">Set</span>();{'\n'}
{'  \n'}
{'  '}<span className="syntax-keyword">for</span> (<span className="syntax-keyword">const</span> node <span className="syntax-keyword">of</span> graph.nodes) {'{\n'}
{'    '}<span className="syntax-keyword">if</span> (!resolved.has(node)) {'{\n'}
{'      '}<span className="syntax-function">walk</span>(node, resolved, seen);{'\n'}
{'    }\n'}
{'  }\n'}
{'  '}<span className="syntax-keyword">return</span> Array.<span className="syntax-function">from</span>(resolved);{'\n'}
{'}'}
                  </code>
                </pre>
              </div>

              {/* Actions */}
              <div className="p-6 pt-4 flex items-center justify-end gap-4 bg-surface-container-low/50">
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors duration-200 border border-transparent">
                  <MaterialIcon icon="share" size={18} />
                  Share Session
                </button>
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-white/5 transition-colors duration-200 border border-white/10 glass-card">
                  <MaterialIcon icon="download" size={18} />
                  Download Code
                </button>
                <button className="flex items-center gap-2 px-6 py-2 rounded-lg font-body-sm text-body-sm text-surface-container-lowest bg-gradient-to-r from-secondary to-secondary-fixed hover:opacity-90 transition-opacity font-semibold shadow-[0_0_15px_rgba(78,222,163,0.3)]">
                  <MaterialIcon icon="content_copy" size={18} />
                  Copy Solution
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
