# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered Japanese message correction application with a LINE-style chat interface. The application supports multiple AI models (OpenAI GPT-4o and Claude 3 Sonnet) for typo correction, honorific enhancement, and business language improvement.

## Development Commands

### Environment Setup
- `cp .env.example .env` - Copy environment template (requires OPENAI_API_KEY and ANTHROPIC_API_KEY)
- `uv sync` - Install Python dependencies using uv
- `npm install` - Install Node.js dependencies

### Development Servers
- `npm run dev:all` - Start both frontend and backend concurrently
- `npm run dev` - Start frontend only (Vite dev server on port 5173)
- `npm run backend` - Start backend only (FastAPI on port 8000)
- `uv run uvicorn main:app --reload --port 8000` - Alternative backend command

### Build and Deploy
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build

### API Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture Overview

### Multi-AI Model Architecture
The application uses an abstract factory pattern to support multiple AI providers:

- **BaseAIService**: Abstract base class defining the interface for AI services
- **AIModelFactory**: Factory class managing AI service instances with lazy loading
- **OpenAIService** & **ClaudeService**: Concrete implementations for different AI providers
- **CorrectionService**: Orchestrates AI calls, user preferences, and history management

### Backend Structure (Python FastAPI)
- **main.py**: FastAPI application with CORS, multiple API endpoints, and database initialization
- **services/correction_service.py**: Main correction coordinator with model selection logic
- **services/ai_model_factory.py**: Factory for managing multiple AI model instances
- **services/openai_service.py** & **services/claude_service.py**: AI provider implementations
- **services/base_ai_service.py**: Abstract interface for AI services
- **database/models.py**: SQLAlchemy models with user preferences and correction history

### Frontend Structure (React + TypeScript)
- **src/components/ChatInterface.tsx**: Main container with header, model selector, and history access
- **src/components/ModelSelector.tsx**: Dropdown component for AI model selection with user preferences
- **src/components/CorrectionHistory.tsx**: Modal displaying paginated correction history
- **src/components/CorrectionModal.tsx**: Modal showing 3 AI-generated correction variants
- **src/components/MessageInput.tsx**: Input field with correction button and UNDO functionality
- **src/services/api.ts**: Comprehensive API client supporting all endpoints

### Key API Flow
1. User selects preferred AI model via ModelSelector (stored in database)
2. User inputs Japanese text in MessageInput
3. "添削" button triggers CorrectionModal with user's preferred model
4. Backend routes request through AIModelFactory to appropriate AI service
5. Returns 3 variants with model attribution and correction reasoning
6. User can view past corrections via CorrectionHistory component
7. Full correction history maintained per user with model tracking

### Database Schema
- **correction_history**: Original/corrected text pairs with ai_model_used tracking
- **user_settings**: User preferences including preferred_ai_model and correction styles
- Automatic table creation on startup with proper indexing

### API Endpoints
- `POST /api/correct` - Text correction with optional model override
- `GET /api/models` - Available AI models with display names
- `POST /api/user/model` - Set user's preferred AI model
- `GET /api/user/{user_id}/settings` - Get user preferences
- `GET /api/user/{user_id}/history` - Paginated correction history

## Technology Stack

- **Frontend**: React + TypeScript + Vite + Axios + Lucide React icons
- **Backend**: Python FastAPI + SQLAlchemy + OpenAI SDK + Anthropic SDK
- **Database**: SQLite with automatic table creation
- **AI Models**: OpenAI GPT-4o, Claude 3 Sonnet
- **Dependency Management**: uv for Python, npm for Node.js

## Current Implementation Status (Phase 2 Complete)

✅ **Phase 1 Features:**
- LINE-style chat UI with message bubbles
- Japanese text correction with 3-variant display
- UNDO functionality with history tracking
- SQLite persistence and CORS-enabled API

✅ **Phase 2 Features:**
- Multiple AI model support (OpenAI + Claude)
- User-specific model preferences with persistent storage  
- Enhanced correction history with pagination and model attribution
- Model selector UI component with responsive design
- Fallback handling for unavailable models

**Architecture Notes:**
- Uses uv for Python dependency management instead of pip/poetry
- Frontend proxy configuration in vite.config.ts routes `/api/*` to backend
- Factory pattern prevents circular imports and enables clean AI provider abstraction
- Database session management with dependency injection pattern
- Japanese-specific prompt engineering optimized for both OpenAI and Claude
- Responsive design with mobile-first approach for all Phase 2 components