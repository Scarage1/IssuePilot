# IssuePilot Frontend

A modern web interface for IssuePilot - AI-powered GitHub issue analysis.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **State Management**: Zustand
- **Data Fetching**: React Query (TanStack Query)
- **Animations**: Framer Motion
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running (see main README)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page (analysis)
│   ├── about/             # About page
│   ├── history/           # Analysis history
│   └── settings/          # Settings page
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── layout/            # Header, Footer
│   ├── common/            # Shared components
│   └── analysis/          # Analysis-specific components
├── hooks/                  # React Query hooks
├── lib/                    # Utilities and API client
├── stores/                 # Zustand stores
└── types/                  # TypeScript types
```

## Features

- 🎨 **Dark/Light Theme**: Toggle between themes
- 📝 **Issue Analysis**: Analyze any GitHub issue
- 📊 **History**: Save and review past analyses
- ⚙️ **Settings**: Configure API URL and GitHub token
- 📤 **Export**: Export results as Markdown or JSON
- 🔄 **Caching**: View and manage API cache

## Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Code Style

- Use TypeScript for all files
- Follow React best practices
- Use Tailwind CSS for styling
- Use shadcn/ui components for consistency

## License

MIT License - see the main LICENSE file.
