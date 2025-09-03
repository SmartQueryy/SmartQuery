# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the frontend codebase.

## Frontend Overview

SmartQuery frontend is a Next.js 14 application with TypeScript and App Router. It provides a dashboard for CSV file management and a natural language query interface for data exploration.

## Development Commands

```bash
npm run dev            # Start development server (http://localhost:3000)
npm run build          # Build for production
npm run start          # Start production server
npm run lint           # Run ESLint
npm run type-check     # TypeScript type checking
npm run test           # Run unit tests (Vitest)
npm run test:e2e       # Run E2E tests (Playwright)
npm run test:integration # Run integration tests
```

## Tech Stack

- **Framework**: Next.js 14 with App Router and TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand for client state
- **HTTP Client**: Axios with centralized API client
- **Charts**: Recharts for data visualization
- **Testing**: Vitest + React Testing Library, Playwright for E2E
- **Icons**: Heroicons

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── dashboard/          # Protected dashboard page
│   ├── login/             # Authentication page
│   ├── workspace/         # CSV query interface
│   │   └── [projectId]/   # Dynamic project workspace
│   ├── layout.tsx         # Root layout with navigation
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # Reusable components
│   ├── ui/                # shadcn/ui components
│   │   ├── button.tsx          # Button with variants
│   │   ├── card.tsx            # Card container component  
│   │   ├── input.tsx           # Input field component
│   │   ├── badge.tsx           # Status badge component
│   │   ├── avatar.tsx          # User avatar component
│   │   ├── dropdown-menu.tsx   # Dropdown menu component
│   │   ├── separator.tsx       # Visual separator
│   │   └── dialog.tsx          # Modal dialog component
│   ├── auth/              # Authentication components
│   │   ├── AuthProvider.tsx    # Auth context provider
│   │   ├── LoginButton.tsx     # Google OAuth login
│   │   └── ProtectedRoute.tsx  # Route protection wrapper
│   ├── dashboard/         # Dashboard-specific components
│   │   ├── bento-grid.tsx      # Dashboard grid layout
│   │   ├── new-project-modal.tsx # Project creation modal
│   │   ├── new-project-tile.tsx  # Create project tile
│   │   └── project-tile.tsx      # Project display tile
│   └── layout/            # Layout components
│       ├── Footer.tsx     # Page footer
│       ├── Navbar.tsx     # Navigation bar
│       └── Sidebar.tsx    # Side navigation
├── lib/                   # Utilities and shared logic
│   ├── api.ts            # Centralized API client
│   ├── auth.ts           # Authentication utilities
│   ├── types.ts          # TypeScript type definitions
│   ├── store.ts          # Main Zustand store
│   └── store/            # Individual stores
│       └── auth.ts       # Authentication store
└── __tests__/            # Test files
    ├── components/       # Component tests
    ├── integration/      # Integration tests
    └── utils/            # Test utilities
```

## Key Architecture Patterns

### 1. Centralized API Client (`lib/api.ts`)
- All backend communication goes through the ApiClient class
- Handles authentication tokens automatically
- Implements retry logic and error handling
- Type-safe using shared API contracts from `../../../shared/api-contract.ts`

### 2. Authentication Flow
- Google OAuth integration via `AuthProvider`
- JWT tokens stored in Zustand auth store
- `ProtectedRoute` component wraps protected pages
- Automatic token refresh and logout handling

### 3. State Management (Zustand)
- Lightweight stores for different concerns
- Auth state in `lib/store/auth.ts`
- Main store aggregator in `lib/store.ts`
- Client-only state management (no SSR state hydration)

### 4. Component Organization
- Feature-based folders (`auth/`, `dashboard/`, `layout/`)
- Reusable UI components with consistent naming
- Props interfaces defined inline or in `lib/types.ts`

## Environment Configuration

Create `.env.local`:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Styling Guidelines

- **Tailwind CSS**: Utility-first approach with custom component classes
- **shadcn/ui**: Premium component library with Radix UI primitives for S-tier SaaS design
- **Design Tokens**: CSS variables defined in `globals.css` for consistent theming
- **Component Variants**: Use `cn()` utility from `@/lib/utils` for conditional styling
- **Responsive Design**: Mobile-first with `sm:`, `md:`, `lg:` breakpoints
- **Theme**: Neutral base color with semantic color system

## API Integration

### API Client Usage
```typescript
import { apiClient } from '@/lib/api';

// All methods return typed responses
const user = await apiClient.auth.getCurrentUser();
const projects = await apiClient.projects.getProjects();
```

### Error Handling
- API client handles network errors automatically
- Retry logic for transient failures
- User-friendly error messages displayed via toast/modal
- Authentication errors trigger automatic logout

## Testing Strategy

### Unit Tests (Vitest)
- Component testing with React Testing Library
- Mock API calls using test utilities
- Focus on user interactions and component behavior

### Integration Tests (Playwright)
- Full user workflows (login, file upload, querying)
- Cross-browser testing
- API integration with real backend responses

### Test Utils (`__tests__/utils/test-utils.tsx`)
- Custom render function with providers
- Mock API client for isolated testing
- Shared test fixtures and helpers

## Authentication

### Google OAuth Flow
1. User clicks login button
2. Redirects to Google OAuth
3. Backend exchanges code for tokens
4. Frontend stores tokens in Zustand store
5. API client uses tokens for authenticated requests

### Route Protection
```typescript
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>
```

## Data Flow

1. **Dashboard**: Lists user projects with upload/delete actions
2. **Project Creation**: Upload CSV → Background processing → Ready for querying
3. **Workspace**: Natural language input → SQL generation → Results display
4. **Charts**: Automatic chart generation for numeric query results

## Development Workflow

1. Start backend services: `cd ../backend && python main.py`
2. Start frontend: `npm run dev`
3. Access at http://localhost:3000
4. Backend API at http://localhost:8000

## Visual Development & Testing

### Design System

The project follows S-Tier SaaS design standards inspired by Stripe, Airbnb, and Linear. All UI development must adhere to:

- **Design Principles**: `/context/design-principles.md` - Comprehensive checklist for world-class UI  
- **Component Library**: shadcn/ui with Radix UI primitives and custom Tailwind configuration

### Quick Visual Check

**IMMEDIATELY after implementing any front-end change:**

1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages` ⚠️

This verification ensures changes meet design standards and user requirements.

## Common Tasks

- **New Component**: Create in appropriate folder with `.tsx` extension
- **New Page**: Add to `src/app/` following App Router conventions
- **API Integration**: Extend `lib/api.ts` with new endpoints
- **State Management**: Add new stores in `lib/store/`
- **Styling**: Use Tailwind utilities and shadcn/ui components from `@/components/ui/`