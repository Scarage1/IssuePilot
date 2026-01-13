import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AnalysisResult } from '@/types/api';

export interface HistoryEntry {
  id: string;
  repo: string;
  issueNumber: number;
  issueTitle?: string;
  result: AnalysisResult;
  timestamp: number;
}

interface HistoryState {
  entries: HistoryEntry[];

  addEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  removeEntry: (id: string) => void;
  clearHistory: () => void;
  getEntry: (id: string) => HistoryEntry | undefined;
}

const MAX_HISTORY_ENTRIES = 50;

export const useHistoryStore = create<HistoryState>()(
  persist(
    (set, get) => ({
      entries: [],

      addEntry: (entry) =>
        set((state) => ({
          entries: [
            {
              ...entry,
              id: crypto.randomUUID(),
              timestamp: Date.now(),
            },
            ...state.entries.slice(0, MAX_HISTORY_ENTRIES - 1),
          ],
        })),

      removeEntry: (id) =>
        set((state) => ({
          entries: state.entries.filter((e) => e.id !== id),
        })),

      clearHistory: () => set({ entries: [] }),

      getEntry: (id) => get().entries.find((e) => e.id === id),
    }),
    {
      name: 'issuepilot-history',
    }
  )
);
