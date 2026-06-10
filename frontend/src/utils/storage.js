const PREFIX = 'opencode_agent_'

export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(PREFIX + key)
      return item ? JSON.parse(item) : defaultValue
    } catch (e) {
      console.warn('Error reading from localStorage', e)
      return defaultValue
    }
  },

  set: (key, value) => {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value))
    } catch (e) {
      console.warn('Error saving to localStorage', e)
    }
  },

  remove: (key) => {
    try {
      localStorage.removeItem(PREFIX + key)
    } catch (e) {
      console.warn('Error removing from localStorage', e)
    }
  },

  clear: () => {
    try {
      Object.keys(localStorage).forEach((key) => {
        if (key.startsWith(PREFIX)) {
          localStorage.removeItem(key)
        }
      })
    } catch (e) {
      console.warn('Error clearing localStorage', e)
    }
  }
}
