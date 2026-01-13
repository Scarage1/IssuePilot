import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export function AnalysisSkeleton() {
  return (
    <div className="space-y-4">
      {/* Header skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-7 w-64" />
        <Skeleton className="h-4 w-48" />
      </div>

      {/* Summary card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-5 w-24" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </CardContent>
      </Card>

      {/* Root cause card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-5 w-40" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </CardContent>
      </Card>

      {/* Solution steps card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-5 w-32" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-6 w-6 rounded-full flex-shrink-0" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Checklist card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-5 w-40" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex gap-2">
                <Skeleton className="h-4 w-4 rounded" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Bottom row */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Skeleton className="h-6 w-16 rounded-full" />
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
