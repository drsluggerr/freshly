import { create } from 'zustand'

interface Action {
  type: string
  payload: any
  timestamp: number
}

interface UndoState {
  past: Action[]
  future: Action[]
  addAction: (action: Action) => void
  undo: () => Action | null
  redo: () => Action | null
  clear: () => void
  canUndo: boolean
  canRedo: boolean
}

export const useUndoStore = create<UndoState>((set, get) => ({
  past: [],
  future: [],
  canUndo: false,
  canRedo: false,

  addAction: (action) => {
    set((state) => ({
      past: [...state.past, action],
      future: [], // Clear redo stack when new action is added
      canUndo: true,
      canRedo: false
    }))
  },

  undo: () => {
    const { past, future } = get()
    if (past.length === 0) return null

    const action = past[past.length - 1]
    const newPast = past.slice(0, -1)

    set({
      past: newPast,
      future: [action, ...future],
      canUndo: newPast.length > 0,
      canRedo: true
    })

    return action
  },

  redo: () => {
    const { past, future } = get()
    if (future.length === 0) return null

    const action = future[0]
    const newFuture = future.slice(1)

    set({
      past: [...past, action],
      future: newFuture,
      canUndo: true,
      canRedo: newFuture.length > 0
    })

    return action
  },

  clear: () => {
    set({
      past: [],
      future: [],
      canUndo: false,
      canRedo: false
    })
  }
}))
