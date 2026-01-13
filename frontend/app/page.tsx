'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
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
    title: 'Smart Summaries',
    description: 'Understand issues in seconds with AI-generated summaries',
  },
  {
    icon: Microscope,
    title: 'Root Cause',
    description: 'AI identifies likely causes of issues',
  },
  {
    icon: ListOrdered,
    title: 'Solution Plans',
    description: 'Step-by-step guidance for fixing issues',
  },
  {
    icon: Link2,
    title: 'Duplicates',
    description: 'Find similar issues automatically',
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
    <div className="container py-8">
      {/* Hero Section - Only show when no result */}
      {!result && !analyzeMutation.isPending && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-primary/10">
              <Rocket className="h-10 w-10 text-primary" />
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            IssuePilot
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            AI-powered GitHub issue analysis for open-source maintainers and contributors
          </p>
        </motion.div>
      )}

      <div className="max-w-3xl mx-auto">
        {/* Input Form */}
        {!result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <IssueInput
              onSubmit={handleSubmit}
              isLoading={analyzeMutation.isPending}
              defaultValues={currentRequest || undefined}
            />
          </motion.div>
        )}

        {/* Error State */}
        {analyzeMutation.isError && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <Card className="border-destructive">
              <CardContent className="flex items-center gap-3 py-4">
                <AlertCircle className="h-5 w-5 text-destructive" />
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

        {/* Loading State */}
        {analyzeMutation.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8"
          >
            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-2 text-muted-foreground">
                <Zap className="h-4 w-4 animate-pulse" />
                <span>Analyzing issue with AI...</span>
              </div>
            </div>
            <AnalysisSkeleton />
          </motion.div>
        )}

        {/* Result Display */}
        {result && currentRequest && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
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

        {/* Features - Only show when no result */}
        {!result && !analyzeMutation.isPending && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-12"
          >
            <h2 className="text-center text-lg font-semibold mb-6">
              What you get
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {features.map(({ icon: Icon, title, description }) => (
                <Card key={title} className="text-center">
                  <CardContent className="pt-6">
                    <Icon className="h-8 w-8 mx-auto mb-2 text-primary" />
                    <h3 className="font-medium mb-1">{title}</h3>
                    <p className="text-xs text-muted-foreground">{description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
