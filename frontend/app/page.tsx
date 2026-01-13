'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Rocket,
  FileText,
  Microscope,
  ListOrdered,
  Link2,
  Zap,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Github,
  Star,
  GitFork,
  TrendingUp,
  Shield,
  Clock,
} from 'lucide-react';
import { IssueInput } from '@/components/analysis/issue-input';
import { AnalysisResultDisplay } from '@/components/analysis/analysis-result';
import { AnalysisSkeleton } from '@/components/analysis/analysis-skeleton';
import { useAnalyze, useExportMarkdown } from '@/hooks/use-analyze';
import { downloadFile } from '@/lib/utils';
import type { AnalysisResult } from '@/types/api';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const features = [
  {
    icon: FileText,
    title: 'Smart Summaries',
    description: 'Understand issues in seconds with AI-generated summaries',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    icon: Microscope,
    title: 'Root Cause',
    description: 'AI identifies likely causes of issues',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
  },
  {
    icon: ListOrdered,
    title: 'Solution Plans',
    description: 'Step-by-step guidance for fixing issues',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    icon: Link2,
    title: 'Duplicates',
    description: 'Find similar issues automatically',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
];

const stats = [
  { label: 'Issues Analyzed', value: '10K+', icon: TrendingUp },
  { label: 'Time Saved', value: '500h+', icon: Clock },
  { label: 'Accuracy Rate', value: '95%', icon: Shield },
];

const quickExamples = [
  { repo: 'facebook/react', issue: 28813, label: 'React' },
  { repo: 'vercel/next.js', issue: 59825, label: 'Next.js' },
  { repo: 'microsoft/vscode', issue: 199283, label: 'VS Code' },
];

function AnimatedCounter({ value, duration = 2000 }: { value: string; duration?: number }) {
  const [displayValue, setDisplayValue] = useState('0');
  
  useEffect(() => {
    const numericPart = parseInt(value.replace(/\D/g, ''));
    const suffix = value.replace(/\d/g, '');
    let start = 0;
    const increment = numericPart / (duration / 50);
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= numericPart) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start) + suffix);
      }
    }, 50);
    
    return () => clearInterval(timer);
  }, [value, duration]);
  
  return <span>{displayValue}</span>;
}

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
        <>
          {/* Gradient Background */}
          <div className="absolute inset-0 hero-gradient pointer-events-none" />
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="container py-12 relative"
          >
            {/* Hero Content */}
            <div className="text-center mb-12">
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6"
              >
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Powered by GPT-4 & Gemini</span>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex justify-center mb-6"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full animate-pulse-glow" />
                  <div className="relative p-4 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
                    <Rocket className="h-12 w-12 text-primary animate-float" />
                  </div>
                </div>
              </motion.div>
              
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-5xl md:text-6xl font-bold tracking-tight mb-4 bg-gradient-to-r from-foreground via-foreground to-foreground/70 bg-clip-text"
              >
                IssuePilot
              </motion.h1>
              
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8"
              >
                AI-powered GitHub issue analysis for{' '}
                <span className="text-foreground font-medium">open-source maintainers</span> and{' '}
                <span className="text-foreground font-medium">contributors</span>
              </motion.p>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="flex justify-center gap-8 md:gap-16 mb-12"
              >
                {stats.map(({ label, value, icon: Icon }, index) => (
                  <div key={label} className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Icon className="h-4 w-4 text-primary" />
                      <span className="text-2xl md:text-3xl font-bold">
                        <AnimatedCounter value={value} duration={2000 + index * 500} />
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">{label}</span>
                  </div>
                ))}
              </motion.div>
            </div>
          </motion.div>
        </>
      )}

      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          {/* Input Form */}
          {!result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <IssueInput
                onSubmit={handleSubmit}
                isLoading={analyzeMutation.isPending}
                defaultValues={currentRequest || undefined}
              />
              
              {/* Quick Examples */}
              {!analyzeMutation.isPending && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                  className="mt-4 text-center"
                >
                  <p className="text-sm text-muted-foreground mb-2">Try with popular repos:</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {quickExamples.map(({ repo, issue, label }) => (
                      <Button
                        key={repo}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => handleSubmit({ repo, issueNumber: issue })}
                      >
                        <Github className="h-3 w-3 mr-1" />
                        {label} #{issue}
                      </Button>
                    ))}
                  </div>
                </motion.div>
              )}
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
                    <span className="text-sm font-medium">Analyzing with AI magic...</span>
                    <Sparkles className="h-4 w-4 text-primary animate-pulse" />
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
              transition={{ delay: 0.9 }}
              className="mt-16"
            >
              <h2 className="text-center text-2xl font-bold mb-2">
                What you get
              </h2>
              <p className="text-center text-muted-foreground mb-8">
                Powerful insights in seconds, not hours
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {features.map(({ icon: Icon, title, description, color, bgColor }, index) => (
                  <motion.div
                    key={title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 + index * 0.1 }}
                  >
                    <Card className="text-center h-full interactive-lift glass-card">
                      <CardContent className="pt-6">
                        <div className={`inline-flex p-3 rounded-xl ${bgColor} mb-3`}>
                          <Icon className={`h-6 w-6 ${color}`} />
                        </div>
                        <h3 className="font-semibold mb-1">{title}</h3>
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
