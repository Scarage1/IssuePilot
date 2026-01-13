'use client';

import { useState } from 'react';
import { Search, Key, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { validateRepoFormat, parseRepoUrl } from '@/lib/utils';

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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Analyze GitHub Issue
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="repo">Repository</Label>
            <Input
              id="repo"
              placeholder="owner/repo or paste GitHub URL"
              value={repo}
              onChange={(e) => handleRepoChange(e.target.value)}
              disabled={isLoading}
              aria-invalid={!!errors.repo}
            />
            {errors.repo && (
              <p className="text-sm text-destructive">{errors.repo}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="issueNumber">Issue Number</Label>
            <Input
              id="issueNumber"
              type="number"
              placeholder="12345"
              value={issueNumber}
              onChange={(e) => setIssueNumber(e.target.value)}
              disabled={isLoading}
              min={1}
              aria-invalid={!!errors.issueNumber}
            />
            {errors.issueNumber && (
              <p className="text-sm text-destructive">{errors.issueNumber}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="token" className="flex items-center gap-1">
              <Key className="h-3 w-3" />
              GitHub Token (optional)
            </Label>
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

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Analyze Issue
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
