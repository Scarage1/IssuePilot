'use client';

import { useState } from 'react';
import { Search, Key, Loader2, Github, Sparkles, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { validateRepoFormat, parseRepoUrl } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface IssueInputProps {
  onSubmit: (data: { repo: string; issueNumber: number; token?: string }) => void;
  isLoading?: boolean;
  defaultValues?: {
    repo?: string;
    issueNumber?: number;
  };
}

export function IssueInput({ onSubmit, isLoading, defaultValues }: IssueInputProps) {
  const [repo, setRepo] = useState(defaultValues?.repo || '');
  const [issueNumber, setIssueNumber] = useState(
    defaultValues?.issueNumber?.toString() || ''
  );
  const [token, setToken] = useState('');
  const [errors, setErrors] = useState<{ repo?: string; issueNumber?: string }>({});
  const [showTokenInput, setShowTokenInput] = useState(false);

  const handleRepoChange = (value: string) => {
    setRepo(value);
    
    // Try to parse GitHub URL
    if (value.includes('github.com')) {
      const parsed = parseRepoUrl(value);
      if (parsed) {
        setRepo(`${parsed.owner}/${parsed.repo}`);
        if (parsed.issueNumber) {
          setIssueNumber(parsed.issueNumber.toString());
        }
      }
    }
  };

  const validate = (): boolean => {
    const newErrors: { repo?: string; issueNumber?: string } = {};

    if (!repo) {
      newErrors.repo = 'Repository is required';
    } else if (!validateRepoFormat(repo)) {
      newErrors.repo = 'Invalid format. Use owner/repo (e.g., facebook/react)';
    }

    if (!issueNumber) {
      newErrors.issueNumber = 'Issue number is required';
    } else if (parseInt(issueNumber, 10) <= 0) {
      newErrors.issueNumber = 'Issue number must be positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        repo,
        issueNumber: parseInt(issueNumber, 10),
        token: token || undefined,
      });
    }
  };

  return (
    <Card className="glass-card overflow-hidden">
      <div className="h-1 bg-gradient-to-r from-primary via-primary/80 to-primary/60" />
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary/10">
            <Github className="h-5 w-5 text-primary" />
          </div>
          <span>Analyze GitHub Issue</span>
          <Sparkles className="h-4 w-4 text-primary ml-auto" />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="repo" className="flex items-center gap-2">
              Repository
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Enter owner/repo or paste a full GitHub URL</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <div className="relative">
              <Github className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="repo"
                placeholder="owner/repo or paste GitHub URL"
                value={repo}
                onChange={(e) => handleRepoChange(e.target.value)}
                disabled={isLoading}
                aria-invalid={!!errors.repo}
                className="pl-10"
              />
            </div>
            {errors.repo && (
              <p className="text-sm text-destructive animate-in">{errors.repo}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="issueNumber">Issue Number</Label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium">#</span>
              <Input
                id="issueNumber"
                type="number"
                placeholder="12345"
                value={issueNumber}
                onChange={(e) => setIssueNumber(e.target.value)}
                disabled={isLoading}
                min={1}
                aria-invalid={!!errors.issueNumber}
                className="pl-8"
              />
            </div>
            {errors.issueNumber && (
              <p className="text-sm text-destructive animate-in">{errors.issueNumber}</p>
            )}
          </div>

          {/* Collapsible Token Input */}
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => setShowTokenInput(!showTokenInput)}
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <Key className="h-3 w-3" />
              <span>{showTokenInput ? 'Hide' : 'Add'} GitHub Token (optional)</span>
            </button>
            
            {showTokenInput && (
              <div className="space-y-2 animate-in">
                <Input
                  id="token"
                  type="password"
                  placeholder="ghp_xxxxxxxxxxxx"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  disabled={isLoading}
                />
                <p className="text-xs text-muted-foreground">
                  For higher API rate limits. Never shared with anyone.
                </p>
              </div>
            )}
          </div>

          <Button 
            type="submit" 
            className="w-full interactive bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70" 
            disabled={isLoading}
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-5 w-5" />
                Analyze Issue
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
