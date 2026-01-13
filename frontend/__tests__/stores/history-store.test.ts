import { act, renderHook } from '@testing-library/react';

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (config: Function) => config,
}));

// Import after mocking
import { useHistoryStore } from '@/stores/history-store';

describe('useHistoryStore', () => {
  beforeEach(() => {
    // Reset store before each test
    act(() => {
      useHistoryStore.getState().clearHistory();
    });
  });

  const mockEntry = {
    repo: 'facebook/react',
    issueNumber: 123,
    issueTitle: 'Test Issue',
    result: {
      summary: 'Test summary',
      root_cause: 'Test root cause',
      solution_steps: ['Step 1', 'Step 2'],
      checklist: ['Check 1'],
      labels: ['bug'],
      similar_issues: [],
    },
  };

  it('should start with empty entries', () => {
    const { result } = renderHook(() => useHistoryStore());
    expect(result.current.entries).toHaveLength(0);
  });

  it('should add a new entry', () => {
    const { result } = renderHook(() => useHistoryStore());

    act(() => {
      result.current.addEntry(mockEntry);
    });

    expect(result.current.entries).toHaveLength(1);
    expect(result.current.entries[0].repo).toBe('facebook/react');
    expect(result.current.entries[0].issueNumber).toBe(123);
    expect(result.current.entries[0].id).toBeDefined();
    expect(result.current.entries[0].timestamp).toBeDefined();
  });

  it('should add entries at the beginning', () => {
    const { result } = renderHook(() => useHistoryStore());

    act(() => {
      result.current.addEntry(mockEntry);
    });

    act(() => {
      result.current.addEntry({ ...mockEntry, issueNumber: 456 });
    });

    expect(result.current.entries).toHaveLength(2);
    expect(result.current.entries[0].issueNumber).toBe(456);
    expect(result.current.entries[1].issueNumber).toBe(123);
  });

  it('should remove an entry by id', () => {
    const { result } = renderHook(() => useHistoryStore());

    act(() => {
      result.current.addEntry(mockEntry);
    });

    const entryId = result.current.entries[0].id;

    act(() => {
      result.current.removeEntry(entryId);
    });

    expect(result.current.entries).toHaveLength(0);
  });

  it('should clear all history', () => {
    const { result } = renderHook(() => useHistoryStore());

    act(() => {
      result.current.addEntry(mockEntry);
      result.current.addEntry({ ...mockEntry, issueNumber: 456 });
      result.current.addEntry({ ...mockEntry, issueNumber: 789 });
    });

    expect(result.current.entries).toHaveLength(3);

    act(() => {
      result.current.clearHistory();
    });

    expect(result.current.entries).toHaveLength(0);
  });

  it('should get an entry by id', () => {
    const { result } = renderHook(() => useHistoryStore());

    act(() => {
      result.current.addEntry(mockEntry);
    });

    const entryId = result.current.entries[0].id;
    const foundEntry = result.current.getEntry(entryId);

    expect(foundEntry).toBeDefined();
    expect(foundEntry?.repo).toBe('facebook/react');
  });

  it('should return undefined for non-existent entry', () => {
    const { result } = renderHook(() => useHistoryStore());

    const foundEntry = result.current.getEntry('non-existent-id');
    expect(foundEntry).toBeUndefined();
  });

  it('should limit entries to MAX_HISTORY_ENTRIES', () => {
    const { result } = renderHook(() => useHistoryStore());

    // Add 55 entries (more than the 50 limit)
    for (let i = 0; i < 55; i++) {
      act(() => {
        result.current.addEntry({ ...mockEntry, issueNumber: i });
      });
    }

    expect(result.current.entries).toHaveLength(50);
    // Newest entry should be first
    expect(result.current.entries[0].issueNumber).toBe(54);
  });
});
