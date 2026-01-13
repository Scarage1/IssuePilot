import { Github, Heart } from 'lucide-react';
import { APP_NAME, GITHUB_REPO_URL } from '@/lib/constants';

export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-14 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          Built with{' '}
          <Heart className="inline-block h-4 w-4 text-red-500" />{' '}
          by{' '}
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium underline underline-offset-4 hover:text-foreground"
          >
            {APP_NAME} Team
          </a>
        </p>
        <div className="flex items-center space-x-4">
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="GitHub"
          >
            <Github className="h-5 w-5" />
          </a>
        </div>
      </div>
    </footer>
  );
}
