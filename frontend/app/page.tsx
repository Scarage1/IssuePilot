'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Rocket,
  FileText,
  Microscope,
  ListOrdered,
  Link2,
  Zap,
  AlertCircle,
} from 'lucide-react';
import { IssueInput } from '@/components/analysis/issue-input';
import { AnalysisResultDisplay } from '@/components/analysis/analysis-result';
import { AnalysisSkeleton } from '@/components/analysis/analysis-skeleton';
import { useAnalyze, useExportMarkdown } from '@/hooks/use-analyze';
import { downloadFile } from '@/lib/utils';
import type { AnalysisResult } from '@/types/api';
import { Card, CardContent } from '@/components/ui/card';

const features = [
  {
    icon: FileText,
    title: 'Issue Summary',
    description: 'Get a clear, concise summary of the issue',
  },
  {
    icon: Microscope,
    title: 'Root Cause Analysis',
    description: 'Understand the likely cause of the problem',
  },
  {
    icon: ListOrdered,
    title: 'Implementation Steps',
    description: 'Actionable steps to resolve the issue',
  },
  {
    icon: Link2,
    title: 'Duplicate Detection',
    description: 'Find related issues in the repository',
  },
];

export default function HomePage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [currentRequest, setCurrentRequest] = useState<{
    repo: string;
    issueNumber: number;
  } | null>(null);

  const analyzeMutation = useAnalyze();
  const exportMutation = useExportMarkdown();

  const handleSubmit = async (data: {
    repo: string;
    issueNumber: number;
    token?: string;
  }) => {
    setCurrentRequest({ repo: data.repo, issueNumber: data.issueNumber });
    
    try {
      const analysisResult = await analyzeMutation.mutateAsync({
        request: {
          repo: data.repo,
          issue_number: data.issueNumber,
          github_token: data.token,
        },
      });
      setResult(analysisResult);
    } catch (error) {
      // Error is handled by the mutation
    }
  };

  const handleExportMarkdown = async () => {
    if (!result) return;
    
    try {
      const markdown = await exportMutation.mutateAsync(result);
      const filename = currentRequest
        ? `${currentRequest.repo.replace('/', '-')}-${currentRequest.issueNumber}.md`
        : 'analysis.md';
      downloadFile(markdown, filename, 'text/markdown');
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleExportJson = () => {
    if (!result || !currentRequest) return;
    
    const filename = `${currentRequest.repo.replace('/', '-')}-${currentRequest.issueNumber}.json`;
    downloadFile(JSON.stringify(result, null, 2), filename, 'application/json');
  };

  const handleAnalyzeAnother = () => {
    setResult(null);
    setCurrentRequest(null);
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section - Only show when no result */}
      {!result && !analyzeMutation.isPending && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="container py-12"
        >
          <div className="text-center mb-10">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="flex justify-center mb-6"
            >
              <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20">
                <Rocket className="h-10 w-10 text-primary" />
              </div>
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl md:text-5xl font-bold tracking-tight mb-4"
            >
              IssuePilot
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-lg text-muted-foreground max-w-xl mx-auto"
            >
              Analyze any GitHub issue with AI. Get summaries, root cause analysis, 
              and implementation steps.
            </motion.p>
          </div>
        </motion.div>
      )}

      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          {/* Input Form */}
          {!result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <IssueInput
                onSubmit={handleSubmit}
                isLoading={analyzeMutation.isPending}
                defaultValues={currentRequest || undefined}
              />
            </motion.div>
          )}

          {/* Error State */}
          <AnimatePresence>
            {analyzeMutation.isError && (
              <motion.div
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                className="mt-4"
              >
                <Card className="border-destructive/50 bg-destructive/5">
                  <CardContent className="flex items-center gap-3 py-4">
                    <div className="p-2 rounded-full bg-destructive/10">
                      <AlertCircle className="h-5 w-5 text-destructive" />
                    </div>
                    <div>
                      <p className="font-medium text-destructive">Analysis Failed</p>
                      <p className="text-sm text-muted-foreground">
                        {analyzeMutation.error instanceof Error
                          ? analyzeMutation.error.message
                          : 'An unexpected error occurred'}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading State */}
          <AnimatePresence>
            {analyzeMutation.isPending && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-8"
              >
                <div className="text-center mb-6">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
                    <Zap className="h-4 w-4 text-primary animate-pulse" />
                    <span className="text-sm font-medium">Analyzing issue...</span>
                  </div>
                </div>
                <AnalysisSkeleton />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Result Display */}
          <AnimatePresence>
            {result && currentRequest && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-8"
              >
                <AnalysisResultDisplay
                  result={result}
                  repo={currentRequest.repo}
                  issueNumber={currentRequest.issueNumber}
                  onExportMarkdown={handleExportMarkdown}
                  onExportJson={handleExportJson}
                  onAnalyzeAnother={handleAnalyzeAnother}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Features - Only show when no result */}
          {!result && !analyzeMutation.isPending && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-16"
            >
              <h2 className="text-center text-xl font-semibold mb-6 text-muted-foreground">
                What you get
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {features.map(({ icon: Icon, title, description }, index) => (
                  <motion.div
                    key={title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                  >
                    <Card className="text-center h-full hover:bg-muted/50 transition-colors">
                      <CardContent className="pt-6">
                        <div className="inline-flex p-3 rounded-lg bg-muted mb-3">
                          <Icon className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <h3 className="font-medium text-sm mb-1">{title}</h3>
                        <p className="text-xs text-muted-foreground">{description}</p>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
