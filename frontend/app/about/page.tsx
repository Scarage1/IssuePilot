'use client';

import { motion } from 'framer-motion';
import {
  Rocket,
  Github,
  Heart,
  Code,
  Users,
  FileText,
  ExternalLink,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GITHUB_REPO_URL, VERSION } from '@/lib/constants';

const features = [
  {
    icon: FileText,
    title: 'Smart Summaries',
    description:
      'AI-powered summaries that help you understand complex issues in seconds.',
  },
  {
    icon: Code,
    title: 'Root Cause Analysis',
    description:
      'Identifies likely causes of issues based on the description and context.',
  },
  {
    icon: Users,
    title: 'Duplicate Detection',
    description:
      'Finds similar issues to avoid duplicate work and link related problems.',
  },
];

const techStack = [
  { name: 'Next.js 14', category: 'Framework' },
  { name: 'React Query', category: 'Data Fetching' },
  { name: 'Tailwind CSS', category: 'Styling' },
  { name: 'Zustand', category: 'State Management' },
  { name: 'FastAPI', category: 'Backend' },
  { name: 'OpenAI GPT-4', category: 'AI' },
];

export default function AboutPage() {
  return (
    <div className="container py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto space-y-8"
      >
        {/* Hero */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-primary/10">
              <Rocket className="h-12 w-12 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-2">About IssuePilot</h1>
          <p className="text-lg text-muted-foreground mb-4">
            AI-powered GitHub issue analysis for the modern developer
          </p>
          <Badge variant="secondary" className="text-sm">
            Version {VERSION}
          </Badge>
        </div>

        {/* Mission */}
        <Card>
          <CardHeader>
            <CardTitle>Our Mission</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              IssuePilot helps open-source maintainers and contributors manage
              GitHub issues more effectively. By leveraging AI, we provide instant
              summaries, identify root causes, suggest labels, and detect duplicate
              issues — saving you hours of manual triage work.
            </p>
          </CardContent>
        </Card>

        {/* Features */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Key Features</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <Card key={title}>
                <CardContent className="pt-6">
                  <Icon className="h-8 w-8 text-primary mb-3" />
                  <h3 className="font-medium mb-2">{title}</h3>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Tech Stack</h2>
          <div className="flex flex-wrap gap-2">
            {techStack.map(({ name, category }) => (
              <Badge key={name} variant="outline" className="py-2 px-3">
                <span className="font-medium">{name}</span>
                <span className="text-muted-foreground ml-2 text-xs">
                  {category}
                </span>
              </Badge>
            ))}
          </div>
        </div>

        {/* Open Source */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-red-500" />
              Open Source
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              IssuePilot is open source and available under the MIT License. We
              welcome contributions from the community!
            </p>
            <div className="flex gap-2">
              <Button asChild>
                <a
                  href={GITHUB_REPO_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="h-4 w-4 mr-2" />
                  View on GitHub
                </a>
              </Button>
              <Button variant="outline" asChild>
                <a
                  href={`${GITHUB_REPO_URL}/issues`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Report Issue
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground">
          Made with{' '}
          <Heart className="inline h-4 w-4 text-red-500" fill="currentColor" />{' '}
          by the IssuePilot Team
        </div>
      </motion.div>
    </div>
  );
}
