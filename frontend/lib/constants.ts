export const APP_NAME = 'IssuePilot';
export const APP_DESCRIPTION = 'AI-powered GitHub issue analysis assistant';
export const APP_VERSION = '1.0.0';
export const VERSION = APP_VERSION;

export const VALID_LABELS = [
  'bug',
  'docs',
  'enhancement',
  'feature',
  'question',
  'good-first-issue',
  'help-wanted',
  'invalid',
  'wontfix',
] as const;

export const LABEL_COLORS: Record<string, string> = {
  bug: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  docs: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  enhancement: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  feature: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  question: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  'good-first-issue': 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
  'help-wanted': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  invalid: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  wontfix: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
};

export const DEFAULT_API_URL = 'http://localhost:8000';

export const GITHUB_REPO_URL = 'https://github.com/Scarage1/IssuePilot';
