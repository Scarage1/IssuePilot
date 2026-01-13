import { act, renderHook } from '@testing-library/react';

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (config: Function) => config,
}));

// Mock constants
jest.mock('@/lib/constants', () => ({
  DEFAULT_API_URL: 'http://localhost:8000',
}));

// Import after mocking
import { useSettingsStore } from '@/stores/settings-store';

describe('useSettingsStore', () => {
  beforeEach(() => {
    // Reset store before each test
    act(() => {
      useSettingsStore.getState().resetSettings();
    });
  });

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useSettingsStore());

    expect(result.current.apiUrl).toBe('http://localhost:8000');
    expect(result.current.githubToken).toBeUndefined();
    expect(result.current.theme).toBe('system');
    expect(result.current.defaultExportFormat).toBe('markdown');
  });

  it('should set API URL', () => {
    const { result } = renderHook(() => useSettingsStore());

    act(() => {
      result.current.setApiUrl('http://api.example.com');
    });

    expect(result.current.apiUrl).toBe('http://api.example.com');
  });

  it('should set GitHub token', () => {
    const { result } = renderHook(() => useSettingsStore());

    act(() => {
      result.current.setGithubToken('ghp_test_token');
    });

    expect(result.current.githubToken).toBe('ghp_test_token');
  });

  it('should clear GitHub token', () => {
    const { result } = renderHook(() => useSettingsStore());

    act(() => {
      result.current.setGithubToken('ghp_test_token');
    });

    act(() => {
      result.current.setGithubToken(undefined);
    });

    expect(result.current.githubToken).toBeUndefined();
  });

  it('should set theme', () => {
    const { result } = renderHook(() => useSettingsStore());

    act(() => {
      result.current.setTheme('dark');
    });

    expect(result.current.theme).toBe('dark');

    act(() => {
      result.current.setTheme('light');
    });

    expect(result.current.theme).toBe('light');
  });

  it('should set default export format', () => {
    const { result } = renderHook(() => useSettingsStore());

    act(() => {
      result.current.setDefaultExportFormat('json');
    });

    expect(result.current.defaultExportFormat).toBe('json');
  });

  it('should reset all settings to defaults', () => {
    const { result } = renderHook(() => useSettingsStore());

    // Change all settings
    act(() => {
      result.current.setApiUrl('http://custom.api.com');
      result.current.setGithubToken('ghp_token');
      result.current.setTheme('dark');
      result.current.setDefaultExportFormat('json');
    });

    // Verify changes
    expect(result.current.apiUrl).toBe('http://custom.api.com');
    expect(result.current.githubToken).toBe('ghp_token');
    expect(result.current.theme).toBe('dark');
    expect(result.current.defaultExportFormat).toBe('json');

    // Reset
    act(() => {
      result.current.resetSettings();
    });

    // Verify reset to defaults
    expect(result.current.apiUrl).toBe('http://localhost:8000');
    expect(result.current.githubToken).toBeUndefined();
    expect(result.current.theme).toBe('system');
    expect(result.current.defaultExportFormat).toBe('markdown');
  });
});
