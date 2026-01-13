'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="container flex flex-col items-center justify-center min-h-[60vh]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex justify-center mb-4">
          <div className="p-4 rounded-full bg-destructive/10">
            <AlertTriangle className="h-12 w-12 text-destructive" />
          </div>
        </div>
        <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
        <p className="text-muted-foreground mb-6 max-w-md">
          {error.message || 'An unexpected error occurred'}
        </p>
        <div className="flex gap-2 justify-center">
          <Button onClick={reset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
          <Button variant="outline" asChild>
            <a href="/">
              <Home className="h-4 w-4 mr-2" />
              Back to Home
            </a>
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
