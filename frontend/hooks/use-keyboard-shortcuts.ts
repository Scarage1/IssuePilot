'use client';

import { useEffect, useCallback } from 'react';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: () => void;
  description: string;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
}

export function useKeyboardShortcuts({
  shortcuts,
  enabled = true,
}: UseKeyboardShortcutsOptions) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Don't trigger shortcuts when typing in inputs
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey || event.metaKey : true;
        const metaMatch = shortcut.metaKey ? event.metaKey : true;
        const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.altKey ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && metaMatch && shiftMatch && altMatch) {
          event.preventDefault();
          shortcut.action();
          return;
        }
      }
    },
    [shortcuts, enabled]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}

// Predefined shortcuts
export const SHORTCUTS = {
  ANALYZE: { key: 'Enter', ctrlKey: true, description: 'Submit analysis' },
  NEW_ANALYSIS: { key: 'n', ctrlKey: true, description: 'New analysis' },
  COPY_SUMMARY: { key: 'c', ctrlKey: true, shiftKey: true, description: 'Copy summary' },
  EXPORT_MARKDOWN: { key: 'e', ctrlKey: true, description: 'Export to markdown' },
  EXPORT_HTML: { key: 'e', ctrlKey: true, shiftKey: true, description: 'Export to HTML' },
  TOGGLE_THEME: { key: 't', ctrlKey: true, description: 'Toggle theme' },
  SHOW_SHORTCUTS: { key: '/', ctrlKey: true, description: 'Show shortcuts' },
  FOCUS_REPO: { key: 'r', ctrlKey: true, description: 'Focus repository input' },
  CLOSE_MODAL: { key: 'Escape', description: 'Close modal/dialog' },
};
