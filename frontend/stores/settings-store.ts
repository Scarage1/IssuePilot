import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { DEFAULT_API_URL } from '@/lib/constants';

interface SettingsState {
  apiUrl: string;
  githubToken: string | undefined;
  theme: 'light' | 'dark' | 'system';
  defaultExportFormat: 'markdown' | 'json';

  setApiUrl: (url: string) => void;
  setGithubToken: (token: string | undefined) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setDefaultExportFormat: (format: 'markdown' | 'json') => void;
  resetSettings: () => void;
}

const initialState = {
  apiUrl: DEFAULT_API_URL,
  githubToken: undefined,
  theme: 'system' as const,
  defaultExportFormat: 'markdown' as const,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...initialState,

      setApiUrl: (url) => set({ apiUrl: url }),
      setGithubToken: (token) => set({ githubToken: token }),
      setTheme: (theme) => set({ theme }),
      setDefaultExportFormat: (format) => set({ defaultExportFormat: format }),
      resetSettings: () => set(initialState),
    }),
    {
      name: 'issuepilot-settings',
    }
  )
);
