import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the settings store
jest.mock('@/stores/settings-store', () => ({
  useSettingsStore: jest.fn((selector) => selector({ githubToken: 'test-token' })),
}));

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    checkRateLimit: jest.fn(),
  },
}));

import { useRateLimit } from '@/hooks/use-rate-limit';
import { apiClient } from '@/lib/api-client';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useRateLimit', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return rate limit info when API call succeeds', async () => {
    const mockData = {
      limit: 5000,
      remaining: 4500,
      reset_at: Math.floor(Date.now() / 1000) + 3600,
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.rateLimitInfo?.limit).toBe(5000);
    expect(result.current.rateLimitInfo?.remaining).toBe(4500);
    expect(result.current.rateLimitInfo?.isLow).toBe(false);
    expect(result.current.rateLimitInfo?.isExhausted).toBe(false);
  });

  it('should indicate low rate limit when below 10%', async () => {
    const mockData = {
      limit: 5000,
      remaining: 400, // 8% remaining
      reset_at: Math.floor(Date.now() / 1000) + 3600,
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.rateLimitInfo?.isLow).toBe(true);
    expect(result.current.rateLimitInfo?.isExhausted).toBe(false);
  });

  it('should indicate exhausted when remaining is 0', async () => {
    const mockData = {
      limit: 5000,
      remaining: 0,
      reset_at: Math.floor(Date.now() / 1000) + 3600,
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.rateLimitInfo?.isExhausted).toBe(true);
    expect(result.current.canMakeRequest()).toBe(false);
  });

  it('should allow requests when rate limit is not exhausted', async () => {
    const mockData = {
      limit: 5000,
      remaining: 1000,
      reset_at: Math.floor(Date.now() / 1000) + 3600,
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.canMakeRequest()).toBe(true);
  });

  it('should calculate percent used correctly', async () => {
    const mockData = {
      limit: 5000,
      remaining: 2500, // 50% remaining = 50% used
      reset_at: Math.floor(Date.now() / 1000) + 3600,
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.rateLimitInfo?.percentUsed).toBe(50);
  });

  it('should format time until reset correctly', async () => {
    const mockData = {
      limit: 5000,
      remaining: 2500,
      reset_at: Math.floor(Date.now() / 1000) + 3700, // About 1 hour
    };
    (apiClient.checkRateLimit as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.rateLimitInfo).not.toBeNull();
    });

    expect(result.current.rateLimitInfo?.resetIn).toMatch(/1h \d+m/);
  });

  it('should return null rateLimitInfo on error', async () => {
    (apiClient.checkRateLimit as jest.Mock).mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.rateLimitInfo).toBeNull();
  });
});
