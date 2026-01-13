import type {
  AnalyzeRequest,
  AnalysisResult,
  HealthResponse,
  CacheStats,
  ExportResponse,
} from '@/types/api';

const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = DEFAULT_API_URL) {
    this.baseUrl = baseUrl;
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let detail: string | undefined;
      try {
        const errorData = await response.json();
        detail = errorData.detail;
      } catch {
        detail = response.statusText;
      }
      throw new APIError(
        `API request failed: ${response.status}`,
        response.status,
        detail
      );
    }

    return response.json();
  }

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async analyze(
    request: AnalyzeRequest,
    options?: { noCache?: boolean }
  ): Promise<AnalysisResult> {
    const headers: Record<string, string> = {};
    
    if (options?.noCache) {
      headers['X-No-Cache'] = 'true';
    }

    return this.request<AnalysisResult>('/analyze', {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });
  }

  async exportMarkdown(analysis: AnalysisResult): Promise<string> {
    const response = await this.request<ExportResponse>('/export', {
      method: 'POST',
      body: JSON.stringify({ analysis }),
    });
    return response.markdown;
  }

  async getCacheStats(): Promise<CacheStats> {
    return this.request<CacheStats>('/cache/stats');
  }

  async clearCache(): Promise<{ message: string; entries_cleared: number }> {
    return this.request('/cache', { method: 'DELETE' });
  }

  async checkRateLimit(token?: string): Promise<{
    limit: number;
    remaining: number;
    reset_at: number;
  }> {
    const url = token ? `/rate-limit?github_token=${token}` : '/rate-limit';
    return this.request(url);
  }
}

export const apiClient = new APIClient();
export default APIClient;
