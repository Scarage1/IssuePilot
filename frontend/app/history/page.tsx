'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  History,
  Trash2,
  ExternalLink,
  Search,
  ChevronRight,
} from 'lucide-react';
import { useHistoryStore, type HistoryEntry } from '@/stores/history-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, downloadFile } from '@/lib/utils';
import { LABEL_COLORS } from '@/lib/constants';

export default function HistoryPage() {
  const { entries, removeEntry, clearHistory } = useHistoryStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);

  const filteredEntries = entries.filter(
    (entry) =>
      entry.repo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.result.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleExportAll = () => {
    const data = JSON.stringify(entries, null, 2);
    downloadFile(data, 'issuepilot-history.json', 'application/json');
  };

  return (
    <div className="container py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <History className="h-6 w-6" />
              Analysis History
            </h1>
            <p className="text-muted-foreground">
              {entries.length} saved {entries.length === 1 ? 'analysis' : 'analyses'}
            </p>
          </div>
          <div className="flex gap-2">
            {entries.length > 0 && (
              <>
                <Button variant="outline" size="sm" onClick={handleExportAll}>
                  Export All
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    if (confirm('Clear all history?')) {
                      clearHistory();
                      setSelectedEntry(null);
                    }
                  }}
                >
                  Clear All
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Search */}
        {entries.length > 0 && (
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by repository or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        )}

        {/* Empty State */}
        {entries.length === 0 && (
          <Card className="text-center py-12">
            <CardContent>
              <History className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">No analysis history</h3>
              <p className="text-muted-foreground mb-4">
                Your analyzed issues will appear here
              </p>
              <Button asChild>
                <a href="/">Analyze an Issue</a>
              </Button>
            </CardContent>
          </Card>
        )}

        {/* History List and Detail View */}
        {entries.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2">
            {/* List */}
            <div className="space-y-2">
              {filteredEntries.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  No results found
                </p>
              ) : (
                filteredEntries.map((entry) => (
                  <Card
                    key={entry.id}
                    className={`cursor-pointer transition-colors hover:bg-accent ${
                      selectedEntry?.id === entry.id ? 'ring-2 ring-primary' : ''
                    }`}
                    onClick={() => setSelectedEntry(entry)}
                  >
                    <CardContent className="flex items-center justify-between py-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium truncate">
                            {entry.repo}
                          </span>
                          <span className="text-muted-foreground">
                            #{entry.issueNumber}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {entry.result.summary.slice(0, 60)}...
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(entry.timestamp)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 ml-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeEntry(entry.id);
                            if (selectedEntry?.id === entry.id) {
                              setSelectedEntry(null);
                            }
                          }}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>

            {/* Detail View */}
            <div className="hidden md:block">
              {selectedEntry ? (
                <Card className="sticky top-20">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>
                        {selectedEntry.repo} #{selectedEntry.issueNumber}
                      </span>
                      <Button variant="ghost" size="icon" asChild>
                        <a
                          href={`https://github.com/${selectedEntry.repo}/issues/${selectedEntry.issueNumber}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-1">Summary</h4>
                      <p className="text-sm text-muted-foreground">
                        {selectedEntry.result.summary}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-1">Root Cause</h4>
                      <p className="text-sm text-muted-foreground">
                        {selectedEntry.result.root_cause}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-1">Labels</h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedEntry.result.labels.map((label) => (
                          <Badge
                            key={label}
                            className={LABEL_COLORS[label] || ''}
                          >
                            {label}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Analyzed {formatDate(selectedEntry.timestamp)}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="sticky top-20">
                  <CardContent className="py-12 text-center">
                    <p className="text-muted-foreground">
                      Select an entry to view details
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
