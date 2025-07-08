SmartQuery MVP - Complete Architecture Documentation
🏗️ File & Folder Structure
smartquery/
├── README.md
├── .gitignore
├── docker-compose.yml
│
├── frontend/                          # Next.js 14 Frontend Application
│   ├── .env.local
│   ├── .env.example
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── images/
│   │       ├── hero-bg.jpg
│   │       └── feature-icons/
│   │
│   └── src/
│       ├── app/                       # Next.js 14 App Router
│       │   ├── globals.css
│       │   ├── layout.tsx             # Root layout with auth provider
│       │   ├── page.tsx               # Landing page (/)
│       │   │
│       │   ├── auth/
│       │   │   └── callback/
│       │   │       └── page.tsx       # OAuth callback handler
│       │   │
│       │   ├── dashboard/
│       │   │   └── page.tsx           # Dashboard with bento grid
│       │   │
│       │   ├── workspace/
│       │   │   └── [projectId]/
│       │   │       └── page.tsx       # Main workspace/chat interface
│       │   │
│       │   └── api/                   # Next.js API Routes
│       │       ├── projects/
│       │       │   ├── route.ts       # POST /api/projects (create)
│       │       │   └── [id]/
│       │       │       ├── route.ts   # GET /api/projects/[id]
│       │       │       └── preview/
│       │       │           └── route.ts # GET /api/projects/[id]/preview
│       │       └── health/
│       │           └── route.ts       # Health check endpoint
│       │
│       ├── components/                # Reusable React Components
│       │   ├── ui/                    # Base UI Components
│       │   │   ├── modal.tsx          # Reusable modal component
│       │   │   ├── button.tsx         # Button variants
│       │   │   ├── input.tsx          # Input field component
│       │   │   ├── file-dropzone.tsx  # Drag & drop file upload
│       │   │   └── loading-spinner.tsx
│       │   │
│       │   ├── layout/                # Layout Components
│       │   │   ├── header.tsx         # Landing page header
│       │   │   └── footer.tsx         # Landing page footer
│       │   │
│       │   ├── auth/                  # Authentication Components
│       │   │   ├── login-button.tsx   # Google OAuth login button
│       │   │   └── user-menu.tsx      # User avatar with dropdown
│       │   │
│       │   ├── landing/               # Landing Page Components
│       │   │   ├── hero-section.tsx   # Hero section with CTA
│       │   │   ├── features-section.tsx # Feature cards grid
│       │   │   └── tech-stack.tsx     # Technology showcase
│       │   │
│       │   ├── dashboard/             # Dashboard Components
│       │   │   ├── dashboard-header.tsx # Dashboard header with user info
│       │   │   ├── bento-grid.tsx     # Responsive bento box layout
│       │   │   ├── new-project-tile.tsx # "+" tile for new projects
│       │   │   ├── project-tile.tsx   # Individual project tile
│       │   │   └── new-project-modal.tsx # Project creation modal
│       │   │
│       │   ├── workspace/             # Workspace Components
│       │   │   ├── workspace-layout.tsx # Main workspace grid layout
│       │   │   ├── workspace-header.tsx # Workspace navigation header
│       │   │   ├── chat-panel.tsx     # Left panel for chat interface
│       │   │   ├── data-panel.tsx     # Right panel for data/results
│       │   │   └── csv-preview.tsx    # CSV data table preview
│       │   │
│       │   ├── chat/                  # Chat Interface Components
│       │   │   ├── chat-container.tsx # Main chat logic container
│       │   │   ├── chat-input.tsx     # Message input with send button
│       │   │   ├── message.tsx        # Base message component
│       │   │   ├── user-message.tsx   # User message styling
│       │   │   ├── ai-message.tsx     # AI response styling
│       │   │   └── typing-indicator.tsx # Loading state for AI responses
│       │   │
│       │   ├── charts/                # Data Visualization Components
│       │   │   ├── bar-chart.tsx      # Bar chart using Recharts
│       │   │   ├── line-chart.tsx     # Line chart component
│       │   │   ├── pie-chart.tsx      # Pie chart component
│       │   │   └── chart-container.tsx # Wrapper for all chart types
│       │   │
│       │   └── results/               # Query Results Components
│       │       ├── query-results.tsx  # Main results display
│       │       ├── data-table.tsx     # Tabular data display
│       │       ├── export-button.tsx  # CSV export functionality
│       │       └── result-tabs.tsx    # Toggle between table/chart view
│       │
│       ├── contexts/                  # React Context Providers
│       │   ├── auth-context.tsx       # Authentication state provider
│       │   └── workspace-context.tsx  # Workspace state provider
│       │
│       ├── hooks/                     # Custom React Hooks
│       │   ├── use-auth.ts            # Authentication hook
│       │   ├── use-projects.ts        # Project data fetching
│       │   ├── use-csv-preview.ts     # CSV preview data hook
│       │   ├── use-chat.ts            # Chat messages and API calls
│       │   └── use-query-results.ts   # Query execution and results
│       │
│       ├── lib/                       # Utility Libraries
│       │   ├── supabase.ts            # Supabase client configuration
│       │   ├── auth.ts                # Authentication helper functions
│       │   ├── storage.ts             # File upload/storage utilities
│       │   ├── api-client.ts          # HTTP client for backend API
│       │   ├── csv-parser.ts          # CSV parsing utilities
│       │   └── utils.ts               # General utility functions
│       │
│       ├── types/                     # TypeScript Type Definitions
│       │   ├── auth.ts                # Authentication types
│       │   ├── project.ts             # Project and dataset types
│       │   ├── chat.ts                # Chat message types
│       │   ├── query.ts               # Query and result types
│       │   └── api.ts                 # API response types
│       │
│       └── styles/                    # Additional Styling
│           ├── globals.css            # Global styles and Tailwind imports
│           └── components.css         # Component-specific styles
│
├── backend/                           # FastAPI Backend Application
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py                        # FastAPI application entry point
│   │
│   ├── api/                           # API Route Handlers
│   │   ├── __init__.py
│   │   ├── query.py                   # POST /api/query - LLM query processing
│   │   ├── health.py                  # GET /api/health - Health check
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── cors.py                # CORS configuration
│   │       └── error_handler.py       # Global error handling
│   │
│   ├── services/                      # Business Logic Services
│   │   ├── __init__.py
│   │   ├── llm_service.py             # OpenAI/LLM integration service
│   │   ├── data_service.py            # CSV processing and SQL execution
│   │   ├── query_service.py           # Natural language to SQL conversion
│   │   └── storage_service.py         # File storage operations
│   │
│   ├── utils/                         # Utility Functions
│   │   ├── __init__.py
│   │   ├── prompts.py                 # LLM prompt templates
│   │   ├── sql_validator.py           # SQL query safety validation
│   │   ├── csv_analyzer.py            # CSV schema analysis
│   │   ├── chart_analyzer.py          # Chart type recommendation
│   │   └── file_utils.py              # File handling utilities
│   │
│   ├── models/                        # Data Models and Schemas
│   │   ├── __init__.py
│   │   ├── query_models.py            # Request/response models for queries
│   │   ├── project_models.py          # Project and dataset models
│   │   └── chart_models.py            # Chart configuration models
│   │
│   └── tests/                         # Backend Tests
│       ├── __init__.py
│       ├── test_llm_service.py
│       ├── test_data_service.py
│       └── test_api.py
│
├── database/                          # Database Scripts and Migrations
│   ├── supabase/
│   │   ├── migrations/
│   │   │   └── 001_initial_schema.sql # Initial database schema
│   │   └── seed/
│   │       └── sample_data.sql        # Sample data for development
│   │
│   └── schemas/
│       ├── projects.sql               # Projects table schema
│       └── users.sql                  # Users table schema (managed by Supabase Auth)
│
├── docs/                              # Documentation
│   ├── api.md                         # API documentation
│   ├── deployment.md                  # Deployment guide
│   ├── development.md                 # Development setup guide
│   └── user-guide.md                  # End-user documentation
│
└── scripts/                           # Development and Deployment Scripts
    ├── setup.sh                       # Initial project setup
    ├── dev.sh                         # Start development environment
    ├── test.sh                        # Run all tests
    └── deploy.sh                      # Deployment script

    🔧 Component Responsibilities
Frontend Components
App Router (src/app/)

Purpose: Next.js 14 App Router for routing and page structure
Responsibilities:

layout.tsx: Root layout with auth provider, global styles, metadata
page.tsx: Landing page with hero section, features, Google OAuth
dashboard/page.tsx: Protected dashboard with bento grid of projects
workspace/[projectId]/page.tsx: Main workspace with chat interface
auth/callback/page.tsx: Handle Google OAuth callback and redirect



UI Components (src/components/ui/)

Purpose: Reusable base components following design system
Responsibilities:

modal.tsx: Reusable modal with backdrop, close functionality
file-dropzone.tsx: Drag-and-drop file upload with validation
button.tsx: Button variants (primary, secondary, ghost, etc.)
input.tsx: Styled input fields with validation states



Dashboard Components (src/components/dashboard/)

Purpose: Dashboard-specific UI components
Responsibilities:

bento-grid.tsx: CSS Grid layout for responsive bento box design
project-tile.tsx: Individual project cards with name, date, preview
new-project-tile.tsx: "+" tile that opens project creation modal
new-project-modal.tsx: Modal form for project name and CSV upload



Workspace Components (src/components/workspace/)

Purpose: Main workspace interface components
Responsibilities:

workspace-layout.tsx: Two-panel layout (chat left, data right)
chat-panel.tsx: Left panel container for chat interface
data-panel.tsx: Right panel with tabs for preview/results
csv-preview.tsx: Table showing CSV headers and sample rows



Chat Components (src/components/chat/)

Purpose: Chat interface for natural language queries
Responsibilities:

chat-container.tsx: Manages message history and API calls
chat-input.tsx: Text input with send button and loading states
user-message.tsx: User message bubbles with proper styling
ai-message.tsx: AI response messages with typing indicators



Backend Components
FastAPI Application (backend/main.py)

Purpose: ASGI application serving LLM processing endpoints
Responsibilities:

Configure CORS for frontend communication
Route registration and middleware setup
Global error handling and logging
Health check endpoints



API Routes (backend/api/)

Purpose: HTTP endpoints for frontend communication
Responsibilities:

query.py: Process natural language queries, return SQL and results
health.py: System health checks and status monitoring



Services (backend/services/)

Purpose: Business logic and external service integration
Responsibilities:

llm_service.py: OpenAI API integration, prompt management
query_service.py: Natural language to SQL conversion pipeline
data_service.py: CSV processing, SQL execution using pandas
storage_service.py: File upload/download from Supabase storage


🗄️ State Management Architecture
Frontend State Strategy
Authentication State (React Context)
// src/contexts/auth-context.tsx
interface AuthContextType {
  user: User | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  isAuthenticated: boolean
}
Location: React Context Provider wrapping entire app
Persistence: Supabase handles session persistence automatically
Scope: Global - available to all components

Project State (Custom Hooks + React Query Pattern)
// src/hooks/use-projects.ts
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => supabase.from('projects').select('*'),
    enabled: !!user
  })
}
Location: Custom hooks using Supabase client
Persistence: PostgreSQL database via Supabase
Scope: Component-level with automatic caching

Chat State (Local Component State)
// src/components/chat/chat-container.tsx
interface ChatState {
  messages: Message[]
  isTyping: boolean
  currentQuery: string
  lastResult: QueryResult | null
}
Location: Chat container component using useState
Persistence: Session-only (resets on page refresh)
Scope: Chat container and children

Workspace State (React Context)
// src/contexts/workspace-context.tsx
interface WorkspaceContextType {
  projectId: string
  projectData: Project | null
  csvPreview: CSVData | null
  activeTab: 'preview' | 'results'
  setActiveTab: (tab: string) => void
}
Location: Workspace-specific context provider
Persistence: Fetched from database, cached during session
Scope: Workspace page and children


Backend State Management
Request-Scoped State

LLM Service: Maintains conversation context per request
Data Service: Loads CSV data into memory for query execution
Query Service: Tracks SQL generation and validation per request

No Persistent State

Backend is stateless - all data stored in Supabase
No sessions or user state maintained on backend
Each request is independent and self-contained



🔗 Service Connections & Data Flow
Authentication Flow
User clicks "Login with Google" → 
Supabase Auth (Google OAuth) → 
OAuth callback page → 
Update auth context → 
Redirect to dashboard

Project Creation Flow
User uploads CSV in modal → 
Next.js API route (/api/projects) → 
Store file in Supabase Storage → 
Create project record in database → 
Redirect to workspace

Query Processing Flow
User types question in chat → 
Frontend sends to FastAPI backend → 
LLM Service (OpenAI) generates SQL → 
Data Service executes SQL on CSV → 
Results returned to frontend → 
Display in results panel

Data Preview Flow
Workspace loads → 
Fetch project from Supabase → 
Next.js API parses CSV from storage → 
Display preview in right panel

🌐 External Service Integration
Supabase Integration
typescript// Frontend connection
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

// Services used:
// - Supabase Auth: Google OAuth, session management
// - Supabase Database: Project metadata storage
// - Supabase Storage: CSV file storage

File Storage Architecture
User uploads CSV → 
Supabase Storage (files bucket) → 
Backend reads via Storage API → 
Pandas processes CSV in memory → 
SQL execution on DataFrame

📊 Data Architecture
Database Schema (Supabase/PostgreSQL)
Projects Table
sqlCREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  csv_filename TEXT NOT NULL,
  csv_path TEXT NOT NULL,
  row_count INTEGER,
  column_count INTEGER,
  columns_metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

Users Table
sql-- Managed automatically by Supabase Auth
-- Includes: id, email, created_at, last_sign_in_at
-- Extended with user_metadata for profile info

File Storage Structure
supabase-storage/
└── files/
    └── {user_id}/
        └── {project_id}/
            └── {original_filename}.csv

CSV Processing Pipeline
CSV Upload → 
File Validation (size, format) → 
Storage in Supabase → 
Schema Analysis (column types, sample data) → 
Metadata Storage in Database → 
Preview Generation

🔄 Real-time Features & Updates
Live Query Processing

Frontend: Show typing indicator while processing
Backend: Stream-like response (single response, not actual streaming)
User Feedback: Loading states, progress indicators

Error Handling Strategy
typescript// Frontend error boundaries
<ErrorBoundary fallback={<ErrorMessage />}>
  <WorkspaceContent />
</ErrorBoundary>

// API error handling
try {
  const result = await processQuery(question)
} catch (error) {
  showErrorToast(error.message)
  logError(error)
}
Performance Optimizations

Frontend: React.memo for expensive components, lazy loading
Backend: CSV caching in memory during session
Database: Proper indexes on user_id and project queries
Storage: CDN for static assets, optimized image loading