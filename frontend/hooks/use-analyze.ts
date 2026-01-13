'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { AnalyzeRequest, AnalysisResult } from '@/types/api';
import { useHistoryStore } from '@/stores/history-store';

export function useAnalyze() {
  const queryClient = useQueryClient();
  const addEntry = useHistoryStore((state) => state.addEntry);

  return useMutation({
    mutationFn: async ({
      request,
      noCache = false,
    }: {
      request: AnalyzeRequest;
      noCache?: boolean;
    }) => {
      return apiClient.analyze(request, { noCache });
    },
    onSuccess: (data, variables) => {
      // Add to history
      addEntry({
        repo: variables.request.repo,
        issueNumber: variables.request.issue_number,
        result: data,
      });

      // Invalidate cache stats
      queryClient.invalidateQueries({ queryKey: ['cache-stats'] });
    },
  });
}

export function useExportMarkdown() {
  return useMutation({
    mutationFn: (analysis: AnalysisResult) => apiClient.exportMarkdown(analysis),
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.health(),
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider fresh for 10 seconds
  });
}

export function useCacheStats() {
  return useQuery({
    queryKey: ['cache-stats'],
    queryFn: () => apiClient.getCacheStats(),
    staleTime: 5000,
  });
}

export function useClearCache() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.clearCache(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cache-stats'] });
    },
  });
}
