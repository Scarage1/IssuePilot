export * from './api';

// History Entry Type
export interface HistoryEntry {
  id: string;
  repo: string;
  issueNumber: number;
  issueTitle?: string;
  result: import('./api').AnalysisResult;
  timestamp: number;
}

// Settings Types
export interface Settings {
  apiUrl: string;
  githubToken?: string;
  theme: 'light' | 'dark' | 'system';
  defaultExportFormat: 'markdown' | 'json';
}
