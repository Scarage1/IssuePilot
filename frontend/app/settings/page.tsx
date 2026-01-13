'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Server,
  Key,
  Palette,
  FileText,
  Check,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { useSettingsStore } from '@/stores/settings-store';
import { useHealth, useCacheStats, useClearCache } from '@/hooks/use-analyze';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DEFAULT_API_URL } from '@/lib/constants';

export default function SettingsPage() {
  const {
    apiUrl,
    githubToken,
    defaultExportFormat,
    setApiUrl,
    setGithubToken,
    setDefaultExportFormat,
    resetSettings,
  } = useSettingsStore();

  const [localApiUrl, setLocalApiUrl] = useState(apiUrl);
  const [localToken, setLocalToken] = useState(githubToken || '');
  const [saved, setSaved] = useState(false);

  const healthQuery = useHealth();
  const cacheStatsQuery = useCacheStats();
  const clearCacheMutation = useClearCache();

  const handleSaveApiUrl = () => {
    setApiUrl(localApiUrl || DEFAULT_API_URL);
    showSaved();
  };

  const handleSaveToken = () => {
    setGithubToken(localToken || undefined);
    showSaved();
  };

  const showSaved = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="container py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto space-y-6"
      >
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Settings className="h-6 w-6" />
            Settings
          </h1>
          <p className="text-muted-foreground">
            Configure IssuePilot to your preferences
          </p>
        </div>

        {/* API Status Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Server className="h-5 w-5" />
              API Status
            </CardTitle>
            <CardDescription>
              Connection status and backend information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Status</span>
              {healthQuery.isLoading ? (
                <Badge variant="secondary">Checking...</Badge>
              ) : healthQuery.isError ? (
                <Badge variant="destructive">Disconnected</Badge>
              ) : (
                <Badge variant="default" className="bg-green-500">
                  <Check className="h-3 w-3 mr-1" />
                  Connected
                </Badge>
              )}
            </div>
            {healthQuery.data && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Version</span>
                  <span className="text-sm text-muted-foreground">
                    {healthQuery.data.version}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">OpenAI API</span>
                  {healthQuery.data.dependencies.openai_api_configured ? (
                    <Badge variant="default" className="bg-green-500">
                      Configured
                    </Badge>
                  ) : (
                    <Badge variant="destructive">Not Configured</Badge>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">GitHub API</span>
                  {healthQuery.data.dependencies.github_api_accessible ? (
                    <Badge variant="default" className="bg-green-500">
                      Accessible
                    </Badge>
                  ) : (
                    <Badge variant="secondary">Limited</Badge>
                  )}
                </div>
              </>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => healthQuery.refetch()}
              disabled={healthQuery.isFetching}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${
                  healthQuery.isFetching ? 'animate-spin' : ''
                }`}
              />
              Refresh
            </Button>
          </CardContent>
        </Card>

        {/* Cache Stats Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Cache Statistics</CardTitle>
            <CardDescription>
              API response caching information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {cacheStatsQuery.data ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Cached Entries</span>
                  <span className="text-sm text-muted-foreground">
                    {cacheStatsQuery.data.size} / {cacheStatsQuery.data.max_size}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">TTL</span>
                  <span className="text-sm text-muted-foreground">
                    {cacheStatsQuery.data.ttl_seconds} seconds
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => clearCacheMutation.mutate()}
                  disabled={
                    clearCacheMutation.isPending || cacheStatsQuery.data.size === 0
                  }
                >
                  Clear Cache
                </Button>
              </>
            ) : cacheStatsQuery.isError ? (
              <p className="text-sm text-muted-foreground">
                Unable to fetch cache stats
              </p>
            ) : (
              <p className="text-sm text-muted-foreground">Loading...</p>
            )}
          </CardContent>
        </Card>

        {/* API URL Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Server className="h-5 w-5" />
              API URL
            </CardTitle>
            <CardDescription>
              Backend server URL for IssuePilot API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiUrl">API Endpoint</Label>
              <Input
                id="apiUrl"
                placeholder={DEFAULT_API_URL}
                value={localApiUrl}
                onChange={(e) => setLocalApiUrl(e.target.value)}
              />
            </div>
            <Button onClick={handleSaveApiUrl}>Save</Button>
          </CardContent>
        </Card>

        {/* GitHub Token Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Key className="h-5 w-5" />
              GitHub Token
            </CardTitle>
            <CardDescription>
              Personal access token for higher API rate limits
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="token">Token</Label>
              <Input
                id="token"
                type="password"
                placeholder="ghp_xxxxxxxxxxxx"
                value={localToken}
                onChange={(e) => setLocalToken(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Get a token at{' '}
                <a
                  href="https://github.com/settings/tokens"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  github.com/settings/tokens
                </a>
              </p>
            </div>
            <Button onClick={handleSaveToken}>Save</Button>
          </CardContent>
        </Card>

        {/* Export Format Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="h-5 w-5" />
              Default Export Format
            </CardTitle>
            <CardDescription>
              Choose your preferred export format
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button
                variant={defaultExportFormat === 'markdown' ? 'default' : 'outline'}
                onClick={() => {
                  setDefaultExportFormat('markdown');
                  showSaved();
                }}
              >
                Markdown
              </Button>
              <Button
                variant={defaultExportFormat === 'json' ? 'default' : 'outline'}
                onClick={() => {
                  setDefaultExportFormat('json');
                  showSaved();
                }}
              >
                JSON
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Reset Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg text-destructive">
              <AlertCircle className="h-5 w-5" />
              Danger Zone
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="destructive"
              onClick={() => {
                if (confirm('Reset all settings to defaults?')) {
                  resetSettings();
                  setLocalApiUrl(DEFAULT_API_URL);
                  setLocalToken('');
                  showSaved();
                }
              }}
            >
              Reset All Settings
            </Button>
          </CardContent>
        </Card>

        {/* Saved Toast */}
        {saved && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center gap-2"
          >
            <Check className="h-4 w-4" />
            Settings saved
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
