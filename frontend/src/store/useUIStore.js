import { create } from 'zustand'
import { storage } from '../utils/storage'

export const useUIStore = create((set) => ({
  // Theme management (dark, light, system, high-contrast)
  theme: storage.get('ui_theme', 'dark'),
  setTheme: (theme) => {
    storage.set('ui_theme', theme)
    set({ theme })
    // Apply theme to document
    if (theme === 'dark' || theme === 'high-contrast') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  },

  // Sidebar toggle for mobile
  isSidebarOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  closeSidebar: () => set({ isSidebarOpen: false }),

  // Settings
  settings: storage.get('ui_settings', {
    autoSave: true,
    model: 'gpt4',
    temperature: 0.7,
    maxRetries: 3
  }),
  updateSettings: (updates) => {
    set((state) => {
      const newSettings = { ...state.settings, ...updates }
      storage.set('ui_settings', newSettings)
      return { settings: newSettings }
    })
  },

  // Toasts
  toasts: [],
  addToast: (message, type = 'info') => {
    const id = Date.now()
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }]
    }))
    // Auto remove after 3s
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter(t => t.id !== id)
      }))
    }, 3000)
  },
  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter(t => t.id !== id)
  })),
}))
