# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Security Policy

**IMPORTANT**: NEVER read the .env file under any circumstances. This file contains sensitive environment variables and API keys that must remain confidential.

## Project Overview

Fluxo is a full-stack AI-powered prompt generator service consisting of:
- **Backend**: FastAPI application with PostgreSQL database for user management and prompt generation
- **Frontend**: Next.js 15 application with React 19 and TypeScript for the user interface

## Development Commands

### Backend (FastAPI)
```bash
# From backend directory
cd backend

# Install dependencies
pip install -r app/requirements.txt

# Local development
cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Create database tables
cd app && python -c "from core.database import create_tables; create_tables()"

# Initialize prompt styles (automatically done on first run)
# Manual seeding if needed:
cd app && python seed_db.py

# Docker development (from backend directory)
docker-compose up -d
docker-compose logs -f fastapi
docker-compose logs -f postgres
docker-compose down

# Reset database (removes all data)
docker-compose down -v
docker-compose up -d
```

### Database Migrations (Alembic)
```bash
# From backend directory
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Show current migration status
alembic current

# Show migration history
alembic history
```

### Frontend (Next.js)
```bash
# From frontend directory
cd frontend

# Install dependencies (using Bun)
bun install

# Development server with Turbopack
bun dev

# Build for production
bun build

# Start production server
bun start

# Lint code
bun lint

# Type checking
bun run build  # Next.js includes TypeScript checking
```

## Architecture Overview

### Backend Architecture
- **FastAPI**: Modern async web framework with automatic OpenAPI documentation at `/docs`
- **PostgreSQL**: Primary database with SQLAlchemy ORM and Alembic migrations
- **JWT Authentication**: Bearer token-based auth with bcrypt password hashing
- **OpenRouter Integration**: LLM API integration using Mistral AI model (`mistralai/mistral-small-3.2-24b-instruct:free`)
- **Email Service**: Resend API integration for email verification and notifications
- **Modular Design**: Separated models, schemas, routers, and core functionality
- **CORS Configuration**: Supports frontend development server at localhost:3000

### Frontend Architecture
- **Next.js 15**: App Router with React 19 and TypeScript
- **Tailwind CSS 4**: Utility-first CSS framework
- **Radix UI**: Component library for consistent UI elements
- **Turbopack**: Fast development build tool

### Database Schema
Core entities:
- **Users**: Authentication, email confirmation, daily request limits (default: 10 requests/day)
- **EmailVerificationCode**: 6-digit codes for email verification (15-minute expiration, 3/hour limit)
- **Prompt Styles**: Reference table for prompt generation styles (Professional, Creative, Analytical, Simple)
- **Prompt Requests**: History of user prompt generation requests with foreign keys to users and styles

## Key Components

### Backend Structure (`backend/app/`)
- `core/`: Core functionality (auth, database, prompt generation)
- `models/`: SQLAlchemy database models
- `schemas/`: Pydantic request/response models
- `routers/`: API endpoints (`/auth`, `/prompts`)
- `main.py`: FastAPI application entry point

### Frontend Structure (`frontend/src/`)
- `app/`: Next.js App Router pages and layouts
- `components/`: Reusable UI components
- `lib/`: Utility functions and configurations

## Environment Configuration

### Backend Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fluxo
POSTGRES_DB=fluxo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# JWT Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter API
OPENROUTER_API_KEY=your-openrouter-key

# Email Service
RESEND_API_KEY=your-resend-key

# Optional CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3001,https://yourdomain.com
```

### API Endpoints
- **Authentication**: `/auth/register`, `/auth/login`, `/auth/me`, `/auth/change-password`
- **Email Verification**: `/auth/confirm-email`, `/auth/resend-confirmation`
- **Prompts**: `/prompts/create`, `/prompts/history`, `/prompts/styles`, `/prompts/limits`
- **Health Check**: `/health`
- **API Documentation**: `/docs` (Swagger UI), `/redoc` (ReDoc)

## Development Notes

### Backend
- All models inherit from `app.models.base.Base`
- Database sessions managed via FastAPI dependency injection (`get_db()`)
- JWT tokens contain user email in "sub" field
- Daily request limits enforced per user (default: 10 requests/day)
- Password hashing with bcrypt before storage
- Email verification uses 6-digit codes with 15-minute expiration
- Rate limiting: 3 verification emails per hour per user
- OpenRouter API integration with 30-second timeout
- Email service uses Resend API with HTML templates

### Frontend
- Uses App Router conventions with TypeScript strict mode
- Path aliases: `@/*` maps to `./src/*`
- Geist fonts loaded via `next/font/google`
- ESLint configured with Next.js and TypeScript presets
- Uses Bun package manager for faster installs
- Turbopack enabled for development server
- API client with comprehensive error handling and validation

### Database Operations
```bash
# Access PostgreSQL in Docker
docker exec -it fluxo-database psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Reset database
docker-compose down -v
docker-compose up -d
```

## Integration Points

The frontend communicates with the backend via REST API calls to generate prompts using OpenRouter's LLM services. Authentication is handled through JWT tokens passed in request headers.

## Development Workflow

### Setting Up the Development Environment
1. **Backend Setup**:
   ```bash
   cd backend
   cp .env.example .env  # Configure your environment variables
   pip install -r app/requirements.txt
   docker-compose up -d  # Start PostgreSQL
   cd app && python -c "from core.database import create_tables; create_tables()"
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   bun install
   # Set NEXT_PUBLIC_API_URL in .env.local if needed
   bun dev
   ```

3. **Full Stack Development**:
   - Backend runs on http://localhost:8000
   - Frontend runs on http://localhost:3000
   - API documentation at http://localhost:8000/docs

### Testing API Endpoints
- Use `/health` endpoint to verify backend is running
- Visit `/docs` for interactive API documentation
- Test authentication flow: register → confirm email → login → access protected routes

### Common Development Tasks
- **Database Reset**: `docker-compose down -v && docker-compose up -d`
- **View Logs**: `docker-compose logs -f fastapi` or `docker-compose logs -f postgres`
- **Email Testing**: Check email verification codes in backend logs (development mode)
- **Migration Management**: Use Alembic commands for database schema changes

### Prompt Generation Testing
The system includes 4 predefined prompt styles:
1. **Professional** (ID: 1): Expert-level responses
2. **Creative** (ID: 2): Innovative and creative approaches
3. **Analytical** (ID: 3): Detailed analysis and structure
4. **Simple** (ID: 4): Easy explanations for beginners

### Troubleshooting
- **OpenRouter API Issues**: Check API key and rate limits
- **Email Service Issues**: Verify Resend API key and email templates
- **Database Connection**: Ensure PostgreSQL is running and DATABASE_URL is correct
- **CORS Issues**: Check CORS_ORIGINS environment variable for additional domains