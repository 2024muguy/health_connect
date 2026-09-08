# HealthConnect AI - Patient Companion Frontend

Production-grade frontend for HealthConnect AI Assistant built with Next.js 14, React 18, TypeScript, and TailwindCSS.

## Overview

The HealthConnect frontend provides a calm, coastal-inspired patient experience with:

- **Dashboard**: Overview of appointments, conversations, and care stats
- **Chat**: AI-powered care assistant with real-time streaming
- **Appointments**: Booking, viewing, and managing visits
- **Clinic**: Services, locations, and contact information
- **Profile**: Patient preferences and information

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14.x | Framework |
| React | 18.x | UI Library |
| TypeScript | 5.x | Type Safety |
| TailwindCSS | 3.x | Styling |
| Zustand | 4.x | State Management |
| TanStack Query | 5.x | Data Fetching |
| Lucide React | Latest | Icons |

## Design System

The visual system uses:
- **Coastal Teal** for primary actions
- **Apricot Warmth** for accents
- **Paper-like Cream** for surfaces
- **DM Sans** for body text
- **Instrument Serif** for display headings
- **Space Mono** for labels and metadata

## Getting Started

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

Project Structure
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/    # Reusable components
│   ├── hooks/         # Custom hooks
│   ├── lib/           # Utilities and API clients
│   ├── stores/        # Zustand stores
│   ├── types/         # TypeScript types
│   └── config/        # Configuration
├── public/            # Static assets
└── tests/             # Test files
Deployment
# Docker
docker build -t healthconnect-frontend .
docker run -p 3000:3000 healthconnect-frontend

# Docker Compose
docker-compose up -d
License
MIT