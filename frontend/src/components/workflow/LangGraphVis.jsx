import { motion, AnimatePresence } from 'framer-motion'
import MaterialIcon from '../ui/MaterialIcon'

const GRAPH_NODES = [
  { id: 'start', label: 'START', type: 'system' },
  { id: 'req', label: 'Requirement Node', type: 'agent' },
  { id: 'gen', label: 'Code Generator Node', type: 'agent' },
  { id: 'exec', label: 'Execution Node', type: 'tool' },
  { id: 'err', label: 'Error Analysis Node', type: 'agent' },
  { id: 'fix', label: 'Fix Node', type: 'agent' },
  { id: 'dec', label: 'Decision Node', type: 'router' },
  { id: 'end', label: 'END', type: 'system' },
]

export default function LangGraphVis({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          exit={{ scale: 0.95 }}
          onClick={e => e.stopPropagation()}
          className="glass-card bg-surface w-full max-w-5xl h-[80vh] rounded-xl shadow-2xl flex flex-col overflow-hidden border border-white/10"
        >
          <div className="p-4 border-b border-white/5 flex items-center justify-between bg-surface-container-low/50">
            <h2 className="font-headline-md text-headline-md font-bold flex items-center gap-2">
              <MaterialIcon icon="account_tree" className="text-primary" />
              LangGraph Architecture
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
              <MaterialIcon icon="close" />
            </button>
          </div>

          <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
            {/* Visual Graph */}
            <div className="flex-1 p-8 overflow-y-auto relative flex flex-col items-center border-r border-white/5 bg-background/50">
              {GRAPH_NODES.map((node, i) => (
                <div key={node.id} className="flex flex-col items-center">
                  <div className={`px-6 py-3 rounded-lg border-2 shadow-lg font-body-sm font-bold w-48 text-center ${
                    node.type === 'system' ? 'bg-surface border-outline-variant text-on-surface' :
                    node.type === 'agent' ? 'bg-primary/20 border-primary text-primary' :
                    node.type === 'tool' ? 'bg-secondary/20 border-secondary text-secondary' :
                    'bg-tertiary-container/20 border-tertiary-container text-tertiary-container'
                  }`}>
                    {node.label}
                  </div>
                  
                  {i < GRAPH_NODES.length - 1 && node.id !== 'dec' && (
                    <div className="w-0.5 h-8 bg-white/20 my-2 flex items-center justify-center relative">
                      <div className="absolute -bottom-2 text-white/40">▼</div>
                    </div>
                  )}

                  {node.id === 'dec' && (
                    <div className="flex w-64 justify-between mt-4 relative">
                      <div className="absolute top-0 left-1/2 w-0.5 h-8 bg-white/20 -translate-x-1/2 -mt-6" />
                      
                      {/* Branch Success */}
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-0.5 bg-success/50 absolute top-0 left-8" />
                        <span className="text-[10px] text-success absolute -top-4 left-12">Success</span>
                        <div className="w-0.5 h-12 bg-success/50" />
                        <div className="absolute bottom-[-16px] text-success/50">▼</div>
                      </div>

                      {/* Branch Retry */}
                      <div className="flex flex-col items-center relative">
                        <div className="w-16 h-0.5 bg-warning/50 absolute top-0 right-8" />
                        <span className="text-[10px] text-warning absolute -top-4 right-12">Retry (Loops back)</span>
                        <div className="w-0.5 h-12 bg-warning/50" />
                        <div className="absolute bottom-[-16px] text-warning/50">▼</div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Source Code representation */}
            <div className="flex-1 bg-black/60 p-4 overflow-y-auto">
              <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4">LANGGRAPH SOURCE</h3>
              <pre className="font-code-base text-code-base text-sm text-primary/80">
{`from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    requirement: str
    code: str
    error: str
    retries: int

workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("requirement", parse_reqs)
workflow.add_node("generator", generate_code)
workflow.add_node("executor", execute_code)
workflow.add_node("error_analyzer", analyze_error)
workflow.add_node("fixer", fix_code)

# Define Edges
workflow.set_entry_point("requirement")
workflow.add_edge("requirement", "generator")
workflow.add_edge("generator", "executor")

def decision_router(state):
    if not state.get("error"):
        return "success"
    if state["retries"] >= 3:
        return "max_retries"
    return "retry"

workflow.add_conditional_edges(
    "executor",
    decision_router,
    {
        "success": END,
        "max_retries": END,
        "retry": "error_analyzer"
    }
)

workflow.add_edge("error_analyzer", "fixer")
workflow.add_edge("fixer", "executor")

app = workflow.compile()
`}
              </pre>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
