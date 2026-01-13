'use client';

import { useEffect, useState } from 'react';
import { Keyboard, Command } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

const shortcuts = [
  { keys: ['/', 'Ctrl', 'K'], description: 'Focus search / Quick analyze' },
  { keys: ['Ctrl', 'Enter'], description: 'Submit analysis' },
  { keys: ['Ctrl', 'Shift', 'M'], description: 'Export as Markdown' },
  { keys: ['Ctrl', 'Shift', 'J'], description: 'Export as JSON' },
  { keys: ['Ctrl', 'Shift', 'H'], description: 'View history' },
  { keys: ['Ctrl', ','], description: 'Open settings' },
  { keys: ['Escape'], description: 'Close dialogs' },
  { keys: ['?'], description: 'Show this help' },
];

function KeyboardKey({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="px-2 py-1 text-xs font-semibold bg-muted border border-border rounded shadow-sm">
      {children}
    </kbd>
  );
}

export function KeyboardShortcuts() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
        const activeElement = document.activeElement;
        const isInput = activeElement instanceof HTMLInputElement || 
                       activeElement instanceof HTMLTextAreaElement;
        if (!isInput) {
          e.preventDefault();
          setOpen(true);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
          <Keyboard className="h-4 w-4" />
          <span className="hidden sm:inline">Shortcuts</span>
          <KeyboardKey>?</KeyboardKey>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Command className="h-5 w-5" />
            Keyboard Shortcuts
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3 mt-4">
          {shortcuts.map(({ keys, description }) => (
            <div
              key={description}
              className="flex items-center justify-between py-2 border-b border-border/50 last:border-0"
            >
              <span className="text-sm text-muted-foreground">{description}</span>
              <div className="flex items-center gap-1">
                {keys.map((key, index) => (
                  <span key={key} className="flex items-center gap-1">
                    <KeyboardKey>{key}</KeyboardKey>
                    {index < keys.length - 1 && (
                      <span className="text-muted-foreground text-xs">+</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground text-center mt-4">
          Press <KeyboardKey>?</KeyboardKey> anywhere to show this dialog
        </p>
      </DialogContent>
    </Dialog>
  );
}
