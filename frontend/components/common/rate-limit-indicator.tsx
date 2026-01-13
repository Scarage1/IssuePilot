'use client';

import { AlertCircle, Clock, Zap } from 'lucide-react';
import { useRateLimit } from '@/hooks/use-rate-limit';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface RateLimitIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

export function RateLimitIndicator({
  className,
  showDetails = false,
}: RateLimitIndicatorProps) {
  const { rateLimitInfo, isLoading, isError } = useRateLimit();

  if (isLoading) {
    return (
      <div className={cn('flex items-center gap-2 text-sm text-muted-foreground', className)}>
        <Zap className="h-4 w-4 animate-pulse" />
        <span>Checking...</span>
      </div>
    );
  }

  if (isError || !rateLimitInfo) {
    return null;
  }

  const getStatusColor = () => {
    if (rateLimitInfo.isExhausted) return 'text-red-500';
    if (rateLimitInfo.isLow) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getProgressColor = () => {
    if (rateLimitInfo.isExhausted) return 'bg-red-500';
    if (rateLimitInfo.isLow) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              'flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm',
              rateLimitInfo.isExhausted && 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950',
              rateLimitInfo.isLow && !rateLimitInfo.isExhausted && 'border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950',
              !rateLimitInfo.isLow && 'border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950',
              className
            )}
          >
            {rateLimitInfo.isExhausted ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : rateLimitInfo.isLow ? (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            ) : (
              <Zap className={cn('h-4 w-4', getStatusColor())} />
            )}
            
            <span className={cn('font-medium', getStatusColor())}>
              {rateLimitInfo.remaining}/{rateLimitInfo.limit}
            </span>

            {showDetails && (
              <>
                <div className="h-4 w-px bg-border" />
                <Clock className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">{rateLimitInfo.resetIn}</span>
              </>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <div className="space-y-2">
            <div className="font-semibold">GitHub API Rate Limit</div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Remaining:</span>
                <span className={getStatusColor()}>{rateLimitInfo.remaining}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Limit:</span>
                <span>{rateLimitInfo.limit}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Resets in:</span>
                <span>{rateLimitInfo.resetIn}</span>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="h-2 w-full rounded-full bg-muted">
              <div
                className={cn('h-full rounded-full transition-all', getProgressColor())}
                style={{ width: `${100 - rateLimitInfo.percentUsed}%` }}
              />
            </div>

            {rateLimitInfo.isExhausted && (
              <p className="text-xs text-red-500">
                Rate limit exhausted. Please wait or add a GitHub token for higher limits.
              </p>
            )}
            {rateLimitInfo.isLow && !rateLimitInfo.isExhausted && (
              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                Running low on API requests. Consider adding a GitHub token.
              </p>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
