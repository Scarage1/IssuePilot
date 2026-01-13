# IssuePilot Frontend Documentation

This document provides a comprehensive guide for building the IssuePilot web frontend.

## Overview

The IssuePilot frontend is a modern web application that provides a user-friendly interface for analyzing GitHub issues. It communicates with the FastAPI backend to deliver AI-powered issue insights.

---

## Tech Stack (Recommended)

| Technology | Purpose | Why |
|------------|---------|-----|
| **Next.js 14+** | Framework | SSR, App Router, great DX |
| **TypeScript** | Language | Type safety, better tooling |
| **Tailwind CSS** | Styling | Utility-first, rapid development |
| **shadcn/ui** | Components | Beautiful, accessible components |
| **React Query** | Data Fetching | Caching, loading states |
| **Zustand** | State Management | Simple, lightweight |
| **Framer Motion** | Animations | Smooth, declarative |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          IssuePilot Frontend                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         Pages (App Router)                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │    │
│  │  │   Home   │  │ Analyze  │  │  History │  │   Settings       │   │    │
│  │  │   Page   │  │   Page   │  │   Page   │  │     Page         │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         Components                                  │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐   │    │
│  │  │  Issue    │  │ Analysis  │  │  Similar  │  │   Export      │   │    │
│  │  │  Input    │  │  Result   │  │  Issues   │  │   Options     │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────────┘   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         Services / Hooks                            │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐   │    │
│  │  │   API     │  │  useAnal- │  │  useHist- │  │   useExport   │   │    │
│  │  │  Client   │  │   yze     │  │   ory     │  │               │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────────┘   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│                    ┌──────────────────────────────┐                        │
│                    │    FastAPI Backend (API)     │                        │
│                    └──────────────────────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   ├── analyze/
│   │   └── page.tsx              # Analyze page
│   ├── history/
│   │   └── page.tsx              # History page
│   ├── settings/
│   │   └── page.tsx              # Settings page
│   └── api/                      # API routes (if needed)
│       └── health/
│           └── route.ts
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   ├── sidebar.tsx
│   │   └── navbar.tsx
│   ├── analysis/
│   │   ├── issue-input.tsx       # Issue input form
│   │   ├── analysis-result.tsx   # Result display
│   │   ├── summary-card.tsx      # Summary section
│   │   ├── root-cause-card.tsx   # Root cause section
│   │   ├── solution-steps.tsx    # Solution steps list
│   │   ├── checklist.tsx         # Developer checklist
│   │   ├── labels-badge.tsx      # Label suggestions
│   │   └── similar-issues.tsx    # Similar issues list
│   ├── common/
│   │   ├── loading-spinner.tsx
│   │   ├── error-boundary.tsx
│   │   ├── copy-button.tsx
│   │   └── theme-toggle.tsx
│   └── export/
│       ├── export-dialog.tsx
│       └── markdown-preview.tsx
├── hooks/
│   ├── use-analyze.ts            # Analysis mutation hook
│   ├── use-history.ts            # History management
│   ├── use-export.ts             # Export functionality
│   └── use-local-storage.ts      # Persistence
├── lib/
│   ├── api-client.ts             # API client
│   ├── utils.ts                  # Utility functions
│   └── constants.ts              # Constants
├── stores/
│   ├── settings-store.ts         # Settings state
│   └── history-store.ts          # History state
├── types/
│   ├── api.ts                    # API types
│   └── index.ts                  # Common types
├── styles/
│   └── globals.css               # Global styles
├── public/
│   ├── logo.svg
│   └── favicon.ico
├── .env.local                    # Environment variables
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

## Pages Specification

### 1. Home Page (`/`)

The landing page with hero section and quick start.

**Features:**
- Hero section with product description
- Quick analyze form (repo + issue input)
- Feature highlights
- Recent analyses (if logged in)
- Call-to-action buttons

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo] IssuePilot                    [Analyze] [History] [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     🚀 IssuePilot                                               │
│     AI-Powered GitHub Issue Analysis                            │
│                                                                 │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  owner/repo              │ Issue #  │ [Analyze →]   │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│     │ 📋       │  │ 🔬       │  │ 🛠️       │  │ 🔗       │    │
│     │ Smart    │  │ Root     │  │ Solution │  │ Duplicate│    │
│     │ Summary  │  │ Cause    │  │ Plans    │  │ Detection│    │
│     └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Analyze Page (`/analyze`)

The main analysis interface.

**Features:**
- Full issue input form
- Real-time analysis with loading states
- Collapsible result sections
- Copy to clipboard functionality
- Export options (Markdown, JSON)
- Similar issues display

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo] IssuePilot                    [Analyze] [History] [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Analyze GitHub Issue                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Repository        │ owner/repo                         │   │
│  │  Issue Number      │ 12345                              │   │
│  │  GitHub Token      │ ••••••••••••• (optional)           │   │
│  │                                           [🔍 Analyze]  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📋 Summary                                    [📋 Copy] │   │
│  │ ─────────────────────────────────────────────────────── │   │
│  │ This issue reports a hydration mismatch error...        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🔬 Root Cause Analysis                        [📋 Copy] │   │
│  │ ─────────────────────────────────────────────────────── │   │
│  │ The likely root cause is that a component...            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🛠️ Solution Steps                                        │   │
│  │ ─────────────────────────────────────────────────────── │   │
│  │ 1. Identify the component causing the mismatch          │   │
│  │ 2. Wrap browser-specific code in useEffect              │   │
│  │ 3. Use dynamic imports with ssr: false                  │   │
│  │ 4. Test with SSR disabled                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ✅ Developer Checklist                                   │   │
│  │ ─────────────────────────────────────────────────────── │   │
│  │ ☐ Read hydration documentation                          │   │
│  │ ☐ Set up local environment                              │   │
│  │ ☐ Reproduce the issue                                   │   │
│  │ ☐ Identify browser-specific code                        │   │
│  │ ☐ Implement fix                                         │   │
│  │ ☐ Test thoroughly                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐  ┌───────────────────────────────┐   │
│  │ 🏷️ Suggested Labels   │  │ 🔗 Similar Issues             │   │
│  │ ┌─────┐ ┌───────────┐│  │ #11234 - Hydration failed... │   │
│  │ │ bug │ │enhancement││  │ #10456 - SSR mismatch with... │   │
│  │ └─────┘ └───────────┘│  └───────────────────────────────┘   │
│  └──────────────────────┘                                       │
│                                                                 │
│  [📄 Export Markdown]  [📦 Export JSON]  [🔄 Analyze Another]  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. History Page (`/history`)

View past analyses (stored in localStorage or backend).

**Features:**
- List of past analyses
- Search and filter
- Quick re-analyze
- Delete entries
- Export all as JSON

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo] IssuePilot                    [Analyze] [History] [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Analysis History                         [🔍 Search] [Export]  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ vercel/next.js #12345           2 hours ago    [→] [🗑️]│   │
│  │ Hydration mismatch error                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ facebook/react #54321           1 day ago      [→] [🗑️]│   │
│  │ useState not updating correctly                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ microsoft/vscode #99999         3 days ago     [→] [🗑️]│   │
│  │ Extension not loading                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Settings Page (`/settings`)

Configure API URL and preferences.

**Features:**
- API URL configuration
- GitHub token storage (encrypted)
- Theme selection (light/dark/system)
- Default export format
- Clear history option

---

## API Integration

### API Client (`lib/api-client.ts`)

```typescript
import { AnalyzeRequest, AnalysisResult, HealthResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseUrl: string;
  
  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }
  
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error('API health check failed');
    return response.json();
  }
  
  async analyze(request: AnalyzeRequest, options?: { noCache?: boolean }): Promise<AnalysisResult> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (options?.noCache) {
      headers['X-No-Cache'] = 'true';
    }
    
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    
    return response.json();
  }
  
  async exportMarkdown(analysis: AnalysisResult): Promise<string> {
    const response = await fetch(`${this.baseUrl}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis }),
    });
    
    if (!response.ok) throw new Error('Export failed');
    const data = await response.json();
    return data.markdown;
  }
  
  async getCacheStats(): Promise<{ size: number; max_size: number; ttl_seconds: number }> {
    const response = await fetch(`${this.baseUrl}/cache/stats`);
    if (!response.ok) throw new Error('Failed to get cache stats');
    return response.json();
  }
  
  async clearCache(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/cache`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Failed to clear cache');
  }
}

export const apiClient = new APIClient();
export default APIClient;
```

### Types (`types/api.ts`)

```typescript
export interface AnalyzeRequest {
  repo: string;
  issue_number: number;
  github_token?: string;
}

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

export interface ExportRequest {
  analysis: AnalysisResult;
}

export interface ExportResponse {
  markdown: string;
}
```

### React Query Hooks (`hooks/use-analyze.ts`)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { AnalyzeRequest, AnalysisResult } from '@/types/api';

export function useAnalyze() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ 
      request, 
      noCache = false 
    }: { 
      request: AnalyzeRequest; 
      noCache?: boolean 
    }) => {
      return apiClient.analyze(request, { noCache });
    },
    onSuccess: (data, variables) => {
      // Invalidate cache stats after analysis
      queryClient.invalidateQueries({ queryKey: ['cache-stats'] });
    },
  });
}

export function useExportMarkdown() {
  return useMutation({
    mutationFn: (analysis: AnalysisResult) => apiClient.exportMarkdown(analysis),
  });
}
```

---

## Component Specifications

### IssueInput Component

```typescript
// components/analysis/issue-input.tsx
interface IssueInputProps {
  onSubmit: (data: { repo: string; issueNumber: number; token?: string }) => void;
  isLoading?: boolean;
  defaultValues?: {
    repo?: string;
    issueNumber?: number;
  };
}
```

**Features:**
- Repository input with format validation (`owner/repo`)
- Issue number input (positive integer)
- Optional GitHub token (password field)
- Submit button with loading state
- Form validation with error messages

### AnalysisResult Component

```typescript
// components/analysis/analysis-result.tsx
interface AnalysisResultProps {
  result: AnalysisResult;
  repo: string;
  issueNumber: number;
  onExport?: (format: 'markdown' | 'json') => void;
  onAnalyzeAnother?: () => void;
}
```

**Features:**
- Collapsible sections for each part
- Copy to clipboard buttons
- Animated reveal on load
- Responsive layout

### SummaryCard Component

```typescript
// components/analysis/summary-card.tsx
interface SummaryCardProps {
  title: string;
  content: string;
  icon: React.ReactNode;
  copyable?: boolean;
}
```

### Checklist Component

```typescript
// components/analysis/checklist.tsx
interface ChecklistProps {
  items: string[];
  editable?: boolean;
  onToggle?: (index: number) => void;
}
```

**Features:**
- Interactive checkboxes (optional)
- Persist state in localStorage
- Copy all items button

---

## State Management

### Settings Store (`stores/settings-store.ts`)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  apiUrl: string;
  githubToken?: string;
  theme: 'light' | 'dark' | 'system';
  defaultExportFormat: 'markdown' | 'json';
  
  setApiUrl: (url: string) => void;
  setGithubToken: (token: string | undefined) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setDefaultExportFormat: (format: 'markdown' | 'json') => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      githubToken: undefined,
      theme: 'system',
      defaultExportFormat: 'markdown',
      
      setApiUrl: (url) => set({ apiUrl: url }),
      setGithubToken: (token) => set({ githubToken: token }),
      setTheme: (theme) => set({ theme }),
      setDefaultExportFormat: (format) => set({ defaultExportFormat: format }),
    }),
    {
      name: 'issuepilot-settings',
    }
  )
);
```

### History Store (`stores/history-store.ts`)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AnalysisResult } from '@/types/api';

interface HistoryEntry {
  id: string;
  repo: string;
  issueNumber: number;
  result: AnalysisResult;
  timestamp: number;
}

interface HistoryState {
  entries: HistoryEntry[];
  
  addEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  removeEntry: (id: string) => void;
  clearHistory: () => void;
}

export const useHistoryStore = create<HistoryState>()(
  persist(
    (set) => ({
      entries: [],
      
      addEntry: (entry) => set((state) => ({
        entries: [
          {
            ...entry,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
          },
          ...state.entries.slice(0, 49), // Keep last 50
        ],
      })),
      
      removeEntry: (id) => set((state) => ({
        entries: state.entries.filter((e) => e.id !== id),
      })),
      
      clearHistory: () => set({ entries: [] }),
    }),
    {
      name: 'issuepilot-history',
    }
  )
);
```

---

## Styling Guidelines

### Color Palette

```css
/* Light Theme */
--background: 0 0% 100%;
--foreground: 222.2 84% 4.9%;
--primary: 222.2 47.4% 11.2%;
--primary-foreground: 210 40% 98%;
--secondary: 210 40% 96.1%;
--accent: 210 40% 96.1%;
--destructive: 0 84.2% 60.2%;
--success: 142.1 76.2% 36.3%;
--warning: 45.4 93.4% 47.5%;
--info: 221.2 83.2% 53.3%;

/* Dark Theme */
--background: 222.2 84% 4.9%;
--foreground: 210 40% 98%;
--primary: 210 40% 98%;
--primary-foreground: 222.2 47.4% 11.2%;
```

### Component Styling

Use Tailwind CSS with consistent spacing:
- `space-y-4` for vertical stacks
- `gap-4` for grids
- `p-6` for card padding
- `rounded-lg` for card borders

---

## Animations

### Page Transitions

```typescript
// Use Framer Motion for smooth transitions
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

### Loading States

```typescript
// Skeleton loading for analysis result
function AnalysisSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-32 bg-muted rounded-lg" />
      <div className="h-24 bg-muted rounded-lg" />
      <div className="h-48 bg-muted rounded-lg" />
    </div>
  );
}
```

---

## Environment Variables

```env
# .env.local

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics
NEXT_PUBLIC_POSTHOG_KEY=your-posthog-key

# Optional: Error Tracking
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

---

## Development Setup

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm

### Installation

```bash
# Clone the repository
git clone https://github.com/Scarage1/IssuePilot.git
cd IssuePilot/frontend

# Install dependencies
pnpm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your settings

# Start development server
pnpm dev

# Open http://localhost:3000
```

### Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:e2e": "playwright test"
  }
}
```

---

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// __tests__/components/issue-input.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { IssueInput } from '@/components/analysis/issue-input';

describe('IssueInput', () => {
  it('validates repo format', async () => {
    const onSubmit = vi.fn();
    render(<IssueInput onSubmit={onSubmit} />);
    
    const repoInput = screen.getByLabelText(/repository/i);
    fireEvent.change(repoInput, { target: { value: 'invalid' } });
    fireEvent.submit(screen.getByRole('form'));
    
    expect(await screen.findByText(/invalid format/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
```

### E2E Tests (Playwright)

```typescript
// e2e/analyze.spec.ts
import { test, expect } from '@playwright/test';

test('analyze issue flow', async ({ page }) => {
  await page.goto('/analyze');
  
  await page.fill('[name="repo"]', 'facebook/react');
  await page.fill('[name="issueNumber"]', '12345');
  await page.click('button[type="submit"]');
  
  // Wait for loading to complete
  await expect(page.locator('[data-testid="analysis-result"]')).toBeVisible({ timeout: 30000 });
  
  // Check sections exist
  await expect(page.locator('[data-testid="summary"]')).toBeVisible();
  await expect(page.locator('[data-testid="root-cause"]')).toBeVisible();
});
```

---

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
pnpm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

---

## Accessibility (a11y)

- All interactive elements are keyboard accessible
- ARIA labels for icons and buttons
- Color contrast meets WCAG 2.1 AA
- Screen reader announcements for loading states
- Focus management for modals and dialogs

---

## Performance Considerations

1. **Code Splitting** - Use dynamic imports for large components
2. **Image Optimization** - Use Next.js Image component
3. **Caching** - Leverage React Query caching
4. **Bundle Size** - Tree-shake unused code
5. **Lazy Loading** - Defer non-critical components

---

## Future Enhancements

- [ ] GitHub OAuth integration
- [ ] Real-time collaboration
- [ ] Browser extension
- [ ] PWA support
- [ ] Multi-language support (i18n)
- [ ] Batch analysis mode
- [ ] Custom prompt templates

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to the frontend.

---

## Related Documentation

- [API Documentation](./api.md)
- [Architecture](./architecture.md)
- [Development Guide](./development.md)
- [Configuration](./configuration.md)
