import { formatDate, validateRepoFormat, parseRepoUrl, truncateText, cn } from '@/lib/utils';

describe('cn (className utility)', () => {
  it('should merge class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should handle conditional classes', () => {
    expect(cn('base', false && 'hidden', true && 'visible')).toBe('base visible');
  });

  it('should merge tailwind classes correctly', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4');
  });
});

describe('formatDate', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-15T12:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should return "Just now" for recent timestamps', () => {
    const now = Date.now();
    expect(formatDate(now)).toBe('Just now');
    expect(formatDate(now - 30000)).toBe('Just now');
  });

  it('should return minutes ago for timestamps within an hour', () => {
    const now = Date.now();
    expect(formatDate(now - 60000)).toBe('1 minute ago');
    expect(formatDate(now - 120000)).toBe('2 minutes ago');
    expect(formatDate(now - 3000000)).toBe('50 minutes ago');
  });

  it('should return hours ago for timestamps within a day', () => {
    const now = Date.now();
    expect(formatDate(now - 3600000)).toBe('1 hour ago');
    expect(formatDate(now - 7200000)).toBe('2 hours ago');
  });

  it('should return days ago for timestamps within a week', () => {
    const now = Date.now();
    expect(formatDate(now - 86400000)).toBe('1 day ago');
    expect(formatDate(now - 172800000)).toBe('2 days ago');
  });
});

describe('validateRepoFormat', () => {
  it('should return true for valid repo formats', () => {
    expect(validateRepoFormat('owner/repo')).toBe(true);
    expect(validateRepoFormat('facebook/react')).toBe(true);
    expect(validateRepoFormat('microsoft/vscode')).toBe(true);
    expect(validateRepoFormat('user-name/repo-name')).toBe(true);
    expect(validateRepoFormat('user_name/repo_name')).toBe(true);
    expect(validateRepoFormat('user.name/repo.name')).toBe(true);
  });

  it('should return false for invalid repo formats', () => {
    expect(validateRepoFormat('')).toBe(false);
    expect(validateRepoFormat('owner')).toBe(false);
    expect(validateRepoFormat('owner/')).toBe(false);
    expect(validateRepoFormat('/repo')).toBe(false);
    expect(validateRepoFormat('owner/repo/extra')).toBe(false);
    expect(validateRepoFormat('https://github.com/owner/repo')).toBe(false);
  });
});

describe('parseRepoUrl', () => {
  it('should parse GitHub URLs without issue number', () => {
    const result = parseRepoUrl('https://github.com/facebook/react');
    expect(result).toEqual({
      owner: 'facebook',
      repo: 'react',
      issueNumber: undefined,
    });
  });

  it('should parse GitHub URLs with issue number', () => {
    const result = parseRepoUrl('https://github.com/facebook/react/issues/123');
    expect(result).toEqual({
      owner: 'facebook',
      repo: 'react',
      issueNumber: 123,
    });
  });

  it('should handle URLs with www prefix', () => {
    const result = parseRepoUrl('https://www.github.com/owner/repo/issues/456');
    expect(result).toEqual({
      owner: 'owner',
      repo: 'repo',
      issueNumber: 456,
    });
  });

  it('should return null for invalid URLs', () => {
    expect(parseRepoUrl('not a url')).toBeNull();
    expect(parseRepoUrl('https://gitlab.com/owner/repo')).toBeNull();
    expect(parseRepoUrl('owner/repo')).toBeNull();
  });
});

describe('truncateText', () => {
  it('should not truncate short text', () => {
    expect(truncateText('Hello', 10)).toBe('Hello');
    expect(truncateText('Short', 5)).toBe('Short');
  });

  it('should truncate long text with ellipsis', () => {
    expect(truncateText('Hello World', 8)).toBe('Hello...');
    expect(truncateText('This is a long text', 10)).toBe('This is...');
  });

  it('should handle edge cases', () => {
    expect(truncateText('', 10)).toBe('');
    expect(truncateText('Hi', 3)).toBe('Hi');
  });
});
