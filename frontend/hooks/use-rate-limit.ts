'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import { useSettingsStore } from '@/stores/settings-store';

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset_at: number;
  resetIn: string;
  percentUsed: number;
  isLow: boolean;
  isExhausted: boolean;
}

function formatTimeUntilReset(resetTimestamp: number): string {
  const now = Math.floor(Date.now() / 1000);
  const secondsUntil = resetTimestamp - now;

  if (secondsUntil <= 0) return 'now';
  if (secondsUntil < 60) return `${secondsUntil}s`;
  if (secondsUntil < 3600) return `${Math.floor(secondsUntil / 60)}m`;
  return `${Math.floor(secondsUntil / 3600)}h ${Math.floor((secondsUntil % 3600) / 60)}m`;
}

export function useRateLimit() {
  const githubToken = useSettingsStore((state) => state.githubToken);
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['rate-limit', githubToken],
    queryFn: async () => {
      const data = await apiClient.checkRateLimit(githubToken);
      return data;
    },
    refetchInterval: 60000, // Refetch every minute
    staleTime: 30000, // Consider fresh for 30 seconds
    retry: false, // Don't retry on failure
  });

  const rateLimitInfo: RateLimitInfo | null = query.data
    ? {
        limit: query.data.limit,
        remaining: query.data.remaining,
        reset_at: query.data.reset_at,
        resetIn: formatTimeUntilReset(query.data.reset_at),
        percentUsed: ((query.data.limit - query.data.remaining) / query.data.limit) * 100,
        isLow: query.data.remaining < query.data.limit * 0.1,
        isExhausted: query.data.remaining === 0,
      }
    : null;

  // Function to check if request can proceed
  const canMakeRequest = useCallback((): boolean => {
    if (!rateLimitInfo) return true; // Allow if we don't have info yet
    return !rateLimitInfo.isExhausted;
  }, [rateLimitInfo]);

  // Optimistically decrement the remaining count after a request
  const decrementRemaining = useCallback(() => {
    queryClient.setQueryData(['rate-limit', githubToken], (oldData: any) => {
      if (!oldData) return oldData;
      return {
        ...oldData,
        remaining: Math.max(0, oldData.remaining - 1),
      };
    });
  }, [queryClient, githubToken]);

  // Refresh rate limit data
  const refreshRateLimit = useCallback(() => {
    return query.refetch();
  }, [query]);

  return {
    ...query,
    rateLimitInfo,
    canMakeRequest,
    decrementRemaining,
    refreshRateLimit,
  };
}
