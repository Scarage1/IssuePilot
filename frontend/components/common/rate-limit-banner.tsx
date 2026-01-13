'use client';

import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';
import { useRateLimit } from '@/hooks/use-rate-limit';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface RateLimitBannerProps {
  className?: string;
}

export function RateLimitBanner({ className }: RateLimitBannerProps) {
  const { rateLimitInfo, isLoading } = useRateLimit();
  const [dismissed, setDismissed] = useState(false);

  if (isLoading || !rateLimitInfo || dismissed) {
    return null;
  }

  // Only show banner when rate limit is exhausted
  if (!rateLimitInfo.isExhausted) {
    return null;
  }

  return (
    <div
      className={cn(
        'flex items-center justify-between gap-4 border-b border-red-200 bg-red-50 px-4 py-3 dark:border-red-900 dark:bg-red-950',
        className
      )}
    >
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-5 w-5 flex-shrink-0 text-red-500" />
        <div className="text-sm">
          <span className="font-semibold text-red-700 dark:text-red-400">
            GitHub API Rate Limit Exceeded
          </span>
          <span className="text-red-600 dark:text-red-300">
            {' '}— Resets in {rateLimitInfo.resetIn}. Add a GitHub token in{' '}
            <a href="/settings" className="underline hover:no-underline">
              Settings
            </a>{' '}
            for higher limits.
          </span>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 flex-shrink-0 text-red-500 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900"
        onClick={() => setDismissed(true)}
        aria-label="Dismiss banner"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
