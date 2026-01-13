import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

export function validateRepoFormat(repo: string): boolean {
  const repoPattern = /^[\w.-]+\/[\w.-]+$/;
  return repoPattern.test(repo);
}

export function parseRepoUrl(url: string): { owner: string; repo: string; issueNumber?: number } | null {
  // Handle GitHub URLs like https://github.com/owner/repo/issues/123
  const githubPattern = /github\.com\/([^/]+)\/([^/]+)(?:\/issues\/(\d+))?/;
  const match = url.match(githubPattern);
  
  if (match) {
    return {
      owner: match[1],
      repo: match[2],
      issueNumber: match[3] ? parseInt(match[3], 10) : undefined,
    };
  }
  
  return null;
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function downloadFile(content: string, filename: string, type: string = 'text/plain') {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}
