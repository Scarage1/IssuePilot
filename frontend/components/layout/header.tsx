'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Rocket, History, Settings, Github, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/common/theme-toggle';
import { APP_NAME, GITHUB_REPO_URL } from '@/lib/constants';

const navLinks = [
  { href: '/', label: 'Analyze', icon: Rocket },
  { href: '/history', label: 'History', icon: History },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Rocket className="h-6 w-6 text-primary" />
            <span className="hidden font-bold sm:inline-block">{APP_NAME}</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          {navLinks.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center space-x-1 transition-colors hover:text-foreground/80',
                pathname === href ? 'text-foreground' : 'text-foreground/60'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="flex flex-1 items-center justify-end space-x-2">
          <nav className="flex items-center space-x-2">
            <Button variant="ghost" size="icon" asChild>
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub repository"
              >
                <Github className="h-5 w-5" />
              </a>
            </Button>
            <ThemeToggle />
            
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </nav>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t">
          <nav className="container py-4 space-y-2">
            {navLinks.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  'flex items-center space-x-2 px-2 py-2 rounded-md transition-colors',
                  pathname === href
                    ? 'bg-accent text-foreground'
                    : 'text-foreground/60 hover:bg-accent hover:text-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
