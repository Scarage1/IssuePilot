// API Request Types

export interface AnalyzeRequest {
  repo: string;
  issue_number: number;
  github_token?: string;
}

export interface ExportRequest {
  analysis: AnalysisResult;
}

// API Response Types

export interface SimilarIssue {
  issue_number: number;
  title: string;
  url: string;
  similarity: number;
}

export interface AnalysisResult {
  summary: string;
  root_cause: string;
  solution_steps: string[];
  checklist: string[];
  labels: string[];
  similar_issues: SimilarIssue[];
}

export interface DependencyStatus {
  openai_api_configured: boolean;
  github_api_accessible: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  dependencies: DependencyStatus;
  cache_size: number;
  cache_ttl: number;
}

export interface ExportResponse {
  markdown: string;
}

export interface CacheStats {
  size: number;
  max_size: number;
  ttl_seconds: number;
  keys: string[];
}

export interface APIErrorResponse {
  detail: string;
}
