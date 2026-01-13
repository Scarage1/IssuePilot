'use client';

import { motion } from 'framer-motion';
import {
  FileText,
  Microscope,
  ListOrdered,
  CheckSquare,
  Tags,
  Link2,
  Download,
  RefreshCw,
} from 'lucide-react';
import type { AnalysisResult } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CopyButton } from '@/components/common/copy-button';
import { LABEL_COLORS } from '@/lib/constants';

interface AnalysisResultProps {
  result: AnalysisResult;
  repo: string;
  issueNumber: number;
  onExportMarkdown?: () => void;
  onExportJson?: () => void;
  onAnalyzeAnother?: () => void;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function AnalysisResultDisplay({
  result,
  repo,
  issueNumber,
  onExportMarkdown,
  onExportJson,
  onAnalyzeAnother,
}: AnalysisResultProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">
            Analysis: {repo} #{issueNumber}
          </h2>
          <p className="text-sm text-muted-foreground">
            AI-powered insights for this issue
          </p>
        </div>
      </motion.div>

      {/* Summary */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between text-lg">
              <span className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                Summary
              </span>
              <CopyButton text={result.summary} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-wrap">
              {result.summary}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Root Cause */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between text-lg">
              <span className="flex items-center gap-2">
                <Microscope className="h-5 w-5 text-yellow-500" />
                Root Cause Analysis
              </span>
              <CopyButton text={result.root_cause} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-wrap">
              {result.root_cause}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Solution Steps */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <ListOrdered className="h-5 w-5 text-green-500" />
              Solution Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-2">
              {result.solution_steps.map((step, index) => (
                <li key={index} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-sm flex items-center justify-center font-medium">
                    {index + 1}
                  </span>
                  <span className="text-muted-foreground">{step}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </motion.div>

      {/* Checklist */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <CheckSquare className="h-5 w-5 text-purple-500" />
              Developer Checklist
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.checklist.map((item, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-muted-foreground">☐</span>
                  <span className="text-muted-foreground">{item}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </motion.div>

      {/* Labels and Similar Issues Row */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2">
        {/* Labels */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Tags className="h-5 w-5 text-orange-500" />
              Suggested Labels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {result.labels.map((label) => (
                <Badge
                  key={label}
                  className={LABEL_COLORS[label] || 'bg-gray-100 text-gray-800'}
                >
                  {label}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Similar Issues */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Link2 className="h-5 w-5 text-cyan-500" />
              Similar Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.similar_issues.length > 0 ? (
              <ul className="space-y-2">
                {result.similar_issues.map((issue) => (
                  <li key={issue.issue_number}>
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm hover:underline text-primary"
                    >
                      #{issue.issue_number}: {issue.title}
                    </a>
                    <span className="text-xs text-muted-foreground ml-2">
                      ({Math.round(issue.similarity * 100)}% similar)
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No similar issues found
              </p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Actions */}
      <motion.div variants={itemVariants} className="flex flex-wrap gap-2">
        {onExportMarkdown && (
          <Button variant="outline" onClick={onExportMarkdown}>
            <Download className="mr-2 h-4 w-4" />
            Export Markdown
          </Button>
        )}
        {onExportJson && (
          <Button variant="outline" onClick={onExportJson}>
            <Download className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
        )}
        {onAnalyzeAnother && (
          <Button variant="secondary" onClick={onAnalyzeAnother}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Analyze Another
          </Button>
        )}
      </motion.div>
    </motion.div>
  );
}
