import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'
import { storage } from '../utils/storage'
import { format } from 'date-fns'

export const useSessionStore = create((set, get) => ({
  sessions: storage.get('sessions', []),
  currentSessionId: null,

  // Load a session
  setCurrentSession: (id) => {
    set({ currentSessionId: id })
  },

  // Create a new session
  createSession: (title = 'New Task') => {
    const newSession = {
      id: uuidv4(),
      title,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      history: [],
      status: 'idle', // idle, active, success, failed
      language: 'Python', // Default
    }
    
    set((state) => {
      const sessions = [newSession, ...state.sessions]
      storage.set('sessions', sessions)
      return { sessions, currentSessionId: newSession.id }
    })
    
    return newSession.id
  },

  // Update session metadata
  updateSession: (id, updates) => {
    set((state) => {
      const sessions = state.sessions.map((s) => 
        s.id === id ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s
      )
      storage.set('sessions', sessions)
      return { sessions }
    })
  },

  // Delete a session
  deleteSession: (id) => {
    set((state) => {
      const sessions = state.sessions.filter(s => s.id !== id)
      storage.set('sessions', sessions)
      return { 
        sessions, 
        currentSessionId: state.currentSessionId === id ? null : state.currentSessionId 
      }
    })
  },

  // Clear all sessions
  clearAllSessions: () => {
    storage.remove('sessions')
    set({ sessions: [], currentSessionId: null })
  },

  // Prompt History Management inside the current session
  addPromptToHistory: (sessionId, promptData) => {
    set((state) => {
      const sessions = state.sessions.map(s => {
        if (s.id === sessionId) {
          const newHistoryItem = {
            id: uuidv4(),
            timestamp: new Date().toISOString(),
            status: 'running',
            ...promptData
          }
          return {
            ...s,
            updatedAt: new Date().toISOString(),
            history: [...s.history, newHistoryItem]
          }
        }
        return s
      })
      storage.set('sessions', sessions)
      return { sessions }
    })
  },

  updatePromptInHistory: (sessionId, promptId, updates) => {
    set((state) => {
      const sessions = state.sessions.map(s => {
        if (s.id === sessionId) {
          return {
            ...s,
            history: s.history.map(h => h.id === promptId ? { ...h, ...updates } : h)
          }
        }
        return s
      })
      storage.set('sessions', sessions)
      return { sessions }
    })
  },
}))
