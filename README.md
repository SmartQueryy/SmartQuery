# SmartQuery MVP

A natural language CSV querying application built with Next.js and FastAPI.

## Architecture

SmartQuery is built as a monorepo with the following structure:

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and daisyUI
- **Backend**: FastAPI with Python for natural language processing
- **Database**: PostgreSQL for metadata storage
- **Storage**: File storage for CSV uploads
- **AI**: OpenAI integration for natural language to SQL conversion

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

### Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd SmartQuery
```

2. Install dependencies:
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Frontend
cp frontend/.env.example frontend/.env.local

# Backend
cp backend/.env.example backend/.env
```

4. Start development servers:
```bash
# Frontend (from frontend directory)
npm run dev

# Backend (from backend directory)
uvicorn main:app --reload
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### Workflow Features

- **Frontend CI**: ESLint, TypeScript checking, testing, and building
- **Backend CI**: Black formatting, isort, flake8 linting, and pytest
- **Integration Tests**: Full-stack testing with PostgreSQL
- **Security Scanning**: Trivy vulnerability scanning and dependency audits
- **Multi-version Testing**: Node.js 18.x/20.x and Python 3.9/3.10/3.11
- **Automated Deployment**: Deploys to staging on main branch

### Running Tests Locally

```bash
# Frontend tests
cd frontend
npm run test
npm run lint
npm run type-check

# Backend tests
cd backend
pytest tests/
black --check .
isort --check-only .
flake8 .
```

## Project Status

✅ **Task 1**: Monorepo structure initialized  
✅ **Task 2**: Environment configuration setup  
✅ **Task 3**: API contract specifications defined  
✅ **Task 4**: CI/CD pipeline implemented  

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure all tests pass locally
4. Create a pull request
5. Wait for CI/CD pipeline to pass
6. Request review

The CI/CD pipeline will automatically run on all pull requests and validate code quality, run tests, and perform security checks.
