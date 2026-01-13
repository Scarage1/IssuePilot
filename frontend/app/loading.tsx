import { LoadingSpinner } from '@/components/common/loading-spinner';

export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <LoadingSpinner size="lg" />
    </div>
  );
}
