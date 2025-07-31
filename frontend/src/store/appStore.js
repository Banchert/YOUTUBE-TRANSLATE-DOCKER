import { create } from 'zustand'; 
export const useAppStore = create((set) => ({ 
  currentTask: null, 
  processingHistory: [], 
  setCurrentTask: (task) => set({ currentTask: task }), 
  addToHistory: (task) => set((state) => ({ 
    processingHistory: [...state.processingHistory, task] 
  })) 
})); 
