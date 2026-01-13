'use client';

import { motion } from 'framer-motion';
import { AlertCircle, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="container flex flex-col items-center justify-center min-h-[60vh]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex justify-center mb-4">
          <div className="p-4 rounded-full bg-destructive/10">
            <AlertCircle className="h-12 w-12 text-destructive" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <p className="text-xl text-muted-foreground mb-6">Page not found</p>
        <Button asChild>
          <a href="/">
            <Home className="h-4 w-4 mr-2" />
            Back to Home
          </a>
        </Button>
      </motion.div>
    </div>
  );
}
