import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'
import { format } from 'date-fns'

const INITIAL_NODES = [
  { id: 'req', label: 'Requirement', status: 'default' },
  { id: 'gen', label: 'Generator', status: 'default' },
  { id: 'exec', label: 'Executor', status: 'default' },
  { id: 'crit', label: 'Critic', status: 'default' }
]

export const useWorkflowStore = create((set, get) => ({
  nodes: INITIAL_NODES,
  timelineLogs: [],
  isExecuting: false,
  retryCount: 0,
  maxRetries: 3,
  
  // Editor state
  currentCode: '',
  terminalOutput: '',
  errorAnalysis: null,

  resetWorkflow: () => {
    set({
      nodes: INITIAL_NODES,
      timelineLogs: [],
      isExecuting: false,
      retryCount: 0,
      currentCode: '',
      terminalOutput: '',
      errorAnalysis: null,
    })
  },

  updateNodeStatus: (nodeId, status) => {
    set(state => ({
      nodes: state.nodes.map(n => 
        n.id === nodeId ? { ...n, status } : n
      )
    }))
  },

  addTimelineLog: (message, type = 'info') => {
    const log = {
      id: uuidv4(),
      timestamp: format(new Date(), 'HH:mm:ss'),
      message,
      type // info, success, error, warning
    }
    set(state => ({
      timelineLogs: [...state.timelineLogs, log]
    }))
  },

  setCode: (code) => set({ currentCode: code }),
  
  appendTerminalOutput: (text) => set(state => ({ 
    terminalOutput: state.terminalOutput + '\n' + text 
  })),
  
  clearTerminal: () => set({ terminalOutput: '' }),

  setErrorAnalysis: (analysis) => set({ errorAnalysis: analysis }),

  incrementRetry: () => set(state => ({ retryCount: state.retryCount + 1 })),

  // Simulation runner for demo purposes
  runMockExecution: async () => {
    const { updateNodeStatus, addTimelineLog, setCode, appendTerminalOutput, setErrorAnalysis } = get()
    
    set({ isExecuting: true, retryCount: 0 })
    addTimelineLog('Prompt Received', 'info')
    
    // Step 1: Requirement
    updateNodeStatus('req', 'active')
    await new Promise(r => setTimeout(r, 1000))
    updateNodeStatus('req', 'done')
    addTimelineLog('Parsed requirements successfully', 'success')
    
    // Step 2: Generator
    updateNodeStatus('gen', 'active')
    addTimelineLog('Generating Code...', 'info')
    await new Promise(r => setTimeout(r, 1500))
    setCode(`def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(1500))`)
    updateNodeStatus('gen', 'done')
    addTimelineLog('Code Generated', 'success')
    
    // Step 3: Executor (Fails first time)
    updateNodeStatus('exec', 'active')
    addTimelineLog('Executing Code...', 'info')
    await new Promise(r => setTimeout(r, 1000))
    
    appendTerminalOutput('$ python fibonacci.py')
    appendTerminalOutput('RecursionError: maximum recursion depth exceeded in comparison')
    updateNodeStatus('exec', 'error')
    addTimelineLog('Error Detected: RecursionError', 'error')
    
    setErrorAnalysis({
      title: 'Stack Overflow Detected',
      confidence: '92%',
      description: 'The recursive implementation exceeds Python\'s default recursion limit.',
      suggestion: 'Refactor to use an iterative approach or memoization.'
    })

    // Step 4: Critic (Retry)
    updateNodeStatus('crit', 'active')
    addTimelineLog('Fixing Code...', 'warning')
    await new Promise(r => setTimeout(r, 2000))
    
    // Re-Generate
    set({ retryCount: 1 })
    setErrorAnalysis(null)
    updateNodeStatus('crit', 'done')
    updateNodeStatus('gen', 'active')
    addTimelineLog('Applying iterative fix...', 'info')
    
    await new Promise(r => setTimeout(r, 1000))
    setCode(`def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n\nprint(fibonacci(1500))`)
    updateNodeStatus('gen', 'done')
    
    // Re-Execute
    updateNodeStatus('exec', 'active')
    addTimelineLog('Re-running Code...', 'info')
    await new Promise(r => setTimeout(r, 1000))
    
    appendTerminalOutput('$ python fibonacci.py\n[Very large number output successfully]')
    updateNodeStatus('exec', 'done')
    addTimelineLog('Execution Successful', 'success')
    
    set({ isExecuting: false })
  }
}))
