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
  ExternalLink,
  Check,
  Sparkles,
  Copy,
} from 'lucide-react';
import type { AnalysisResult } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CopyButton } from '@/components/common/copy-button';
import { LABEL_COLORS } from '@/lib/constants';
import { useState } from 'react';

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
      staggerChildren: 0.08,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function ChecklistItem({ item, index }: { item: string; index: number }) {
  const [checked, setChecked] = useState(false);
  
  return (
    <li 
      className={`flex items-start gap-3 p-2 rounded-lg transition-all cursor-pointer hover:bg-muted/50 ${checked ? 'bg-green-500/5' : ''}`}
      onClick={() => setChecked(!checked)}
    >
      <span className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
        checked 
          ? 'bg-green-500 border-green-500 text-white' 
          : 'border-muted-foreground/30 hover:border-primary'
      }`}>
        {checked && <Check className="h-3 w-3" />}
      </span>
      <span className={`text-sm transition-all ${checked ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
        {item}
      </span>
    </li>
  );
}

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
      {/* Success Banner */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-green-500/10 border border-green-500/20">
          <Sparkles className="h-4 w-4 text-green-500" />
          <span className="text-sm font-medium text-green-600 dark:text-green-400">
            Analysis complete! Here are your insights.
          </span>
        </div>
      </motion.div>

      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold flex items-center gap-2">
            Analysis: {repo}
            <Badge variant="secondary">#{issueNumber}</Badge>
          </h2>
          <p className="text-sm text-muted-foreground">
            AI-powered insights for this issue
          </p>
        </div>
        <a
          href={`https://github.com/${repo}/issues/${issueNumber}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-primary hover:underline flex items-center gap-1"
        >
          View on GitHub
          <ExternalLink className="h-3 w-3" />
        </a>
      </motion.div>

      {/* Summary */}
      <motion.div variants={itemVariants}>
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-blue-500 to-blue-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between text-lg">
              <span className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-blue-500/10">
                  <FileText className="h-4 w-4 text-blue-500" />
                </div>
                Summary
              </span>
              <CopyButton text={result.summary} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
              {result.summary}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Root Cause */}
      <motion.div variants={itemVariants}>
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-yellow-500 to-orange-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between text-lg">
              <span className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-yellow-500/10">
                  <Microscope className="h-4 w-4 text-yellow-500" />
                </div>
                Root Cause Analysis
              </span>
              <CopyButton text={result.root_cause} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
              {result.root_cause}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Solution Steps */}
      <motion.div variants={itemVariants}>
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-green-500 to-emerald-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <div className="p-1.5 rounded-lg bg-green-500/10">
                <ListOrdered className="h-4 w-4 text-green-500" />
              </div>
              Solution Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3">
              {result.solution_steps.map((step, index) => (
                <li key={index} className="flex gap-3 group">
                  <span className="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 text-white text-sm flex items-center justify-center font-medium shadow-sm">
                    {index + 1}
                  </span>
                  <span className="text-muted-foreground pt-0.5 group-hover:text-foreground transition-colors">
                    {step}
                  </span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </motion.div>

      {/* Checklist */}
      <motion.div variants={itemVariants}>
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-purple-500 to-pink-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <div className="p-1.5 rounded-lg bg-purple-500/10">
                <CheckSquare className="h-4 w-4 text-purple-500" />
              </div>
              Developer Checklist
              <span className="text-xs font-normal text-muted-foreground ml-2">
                (click to check off)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {result.checklist.map((item, index) => (
                <ChecklistItem key={index} item={item} index={index} />
              ))}
            </ul>
          </CardContent>
        </Card>
      </motion.div>

      {/* Labels and Similar Issues Row */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2">
        {/* Labels */}
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-orange-500 to-red-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <div className="p-1.5 rounded-lg bg-orange-500/10">
                <Tags className="h-4 w-4 text-orange-500" />
              </div>
              Suggested Labels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {result.labels.map((label) => (
                <Badge
                  key={label}
                  className={`${LABEL_COLORS[label] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'} transition-transform hover:scale-105`}
                >
                  {label}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Similar Issues */}
        <Card className="glass-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-cyan-500 to-blue-400" />
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <div className="p-1.5 rounded-lg bg-cyan-500/10">
                <Link2 className="h-4 w-4 text-cyan-500" />
              </div>
              Similar Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.similar_issues.length > 0 ? (
              <ul className="space-y-2">
                {result.similar_issues.map((issue) => (
                  <li key={issue.issue_number} className="group">
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <span className="text-sm text-primary group-hover:underline flex items-center gap-1">
                        #{issue.issue_number}: {issue.title}
                        <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </span>
                      <Badge variant="secondary" className="text-xs">
                        {Math.round(issue.similarity * 100)}%
                      </Badge>
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No similar issues found
              </p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Actions */}
      <motion.div variants={itemVariants} className="flex flex-wrap gap-3 pt-4">
        {onExportMarkdown && (
          <Button variant="outline" onClick={onExportMarkdown} className="interactive">
            <Download className="mr-2 h-4 w-4" />
            Export Markdown
          </Button>
        )}
        {onExportJson && (
          <Button variant="outline" onClick={onExportJson} className="interactive">
            <Download className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
        )}
        {onAnalyzeAnother && (
          <Button onClick={onAnalyzeAnother} className="interactive bg-gradient-to-r from-primary to-primary/80">
            <RefreshCw className="mr-2 h-4 w-4" />
            Analyze Another Issue
          </Button>
        )}
      </motion.div>
    </motion.div>
  );
}
