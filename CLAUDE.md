# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered Japanese message correction application with a LINE-style chat interface. The application supports multiple AI models (OpenAI GPT-4o, Claude 3 Sonnet, and Local LLMs via Ollama) for typo correction, honorific enhancement, and business language improvement with advanced features including caching, error handling, and mobile optimization.

## Development Commands

### Environment Setup
- `cp .env.example .env` - Copy environment template (requires OPENAI_API_KEY and ANTHROPIC_API_KEY)
- `uv sync` - Install Python dependencies using uv (includes Ollama and Redis support)
- `npm install` - Install Node.js dependencies

### Development Servers
- `npm run dev:all` - Start both frontend and backend concurrently
- `npm run dev` - Start frontend only (Vite dev server on port 5173)
- `npm run backend` - Start backend only (FastAPI on port 8000)
- `uv run uvicorn main:app --reload --port 8000` - Alternative backend command

### Build and Deploy
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build

### Validation Commands
- `python -m py_compile main.py` - Check backend syntax
- `python -m py_compile services/*.py` - Check all service files
- `npm run build` - Validate TypeScript compilation

### API Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture Overview

### Multi-AI Model Architecture with Advanced Features
The application uses an abstract factory pattern with comprehensive error handling and performance optimization:

- **BaseAIService**: Abstract base class defining the interface for AI services
- **AIModelFactory**: Factory class managing AI service instances with lazy loading
- **OpenAIService**, **ClaudeService**, **LocalLLMService**: AI provider implementations
- **CorrectionService**: Orchestrates AI calls, caching, error handling, and user preferences
- **ErrorHandler**: Circuit breaker pattern with automatic fallbacks and retry logic
- **CacheService**: Redis-based caching with in-memory fallback

### Backend Structure (Python FastAPI)
- **main.py**: FastAPI application with CORS, admin endpoints, batch processing, and health monitoring
- **services/correction_service.py**: Main coordinator with caching, error handling, and async operations
- **services/ai_model_factory.py**: Factory managing OpenAI, Claude, and local LLM instances
- **services/openai_service.py**, **claude_service.py**, **local_llm_service.py**: AI provider implementations
- **services/base_ai_service.py**: Abstract interface for AI services
- **services/cache_service.py**: Redis/in-memory caching with performance metrics
- **services/error_handler.py**: Circuit breaker, retry logic, and service health monitoring
- **database/models.py**: SQLAlchemy models with user preferences and correction history

### Frontend Structure (React + TypeScript)
- **src/components/ChatInterface.tsx**: Main container with mobile-responsive header and layout
- **src/components/ModelSelector.tsx**: AI model selection dropdown with user preferences
- **src/components/CorrectionStyleSelector.tsx**: Six correction styles (Standard, Formal, Casual, Business, Error Focus, Concise)
- **src/components/CorrectionHistory.tsx**: Paginated correction history modal
- **src/components/CorrectionModal.tsx**: Mobile-optimized modal showing correction variants with style support
- **src/components/MessageInput.tsx**: Input field with style selector, correction button, and UNDO functionality
- **src/services/api.ts**: Comprehensive API client with batch processing and admin endpoints

### Key API Flow with Advanced Features
1. User selects preferred AI model via ModelSelector (stored in database)
2. User selects correction style via CorrectionStyleSelector (6 options available)
3. User inputs Japanese text in MessageInput with mobile-optimized interface
4. "添削" button triggers CorrectionModal with caching check and error handling
5. Backend uses ErrorHandler for retry logic and automatic fallbacks between OpenAI/Claude/Local LLM
6. CacheService checks Redis (or in-memory) for cached results before AI processing
7. Returns 3 variants with model attribution, processing time, and correction reasoning
8. Results cached for future requests with TTL and style-aware keys
9. User can view correction history with pagination and model tracking

### Database Schema
- **correction_history**: Original/corrected text pairs with ai_model_used tracking
- **user_settings**: User preferences including preferred_ai_model and correction styles
- Automatic table creation on startup with proper indexing

### API Endpoints

#### Core Functionality
- `POST /api/correct` - Text correction with model, style, and caching support
- `POST /api/correct/batch` - Batch correction processing for multiple requests
- `GET /api/models` - Available AI models (OpenAI, Claude, Local LLM)
- `POST /api/user/model` - Set user's preferred AI model
- `GET /api/user/{user_id}/settings` - Get user preferences
- `GET /api/user/{user_id}/history` - Paginated correction history with model tracking

#### Admin & Monitoring
- `GET /api/admin/health` - Service health status and circuit breaker state
- `GET /api/admin/cache-stats` - Cache performance metrics (Redis/in-memory)
- `POST /api/admin/clear-cache` - Manual cache invalidation
- `POST /api/admin/reset-circuit-breaker/{service_name}` - Reset specific service circuit breaker

## Technology Stack

- **Frontend**: React + TypeScript + Vite + Axios + Lucide React icons
- **Backend**: Python FastAPI + SQLAlchemy + OpenAI SDK + Anthropic SDK + Ollama SDK
- **Database**: SQLite with automatic table creation and async operations
- **Caching**: Redis with in-memory fallback support
- **AI Models**: OpenAI GPT-4o, Claude 3 Sonnet, Local LLMs (Qwen2.5, Llama3.2, Gemma2 via Ollama)
- **Dependency Management**: uv for Python, npm for Node.js
- **Error Handling**: Circuit breaker pattern with exponential backoff

## Current Implementation Status (Phase 3 Complete)

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

✅ **Phase 3 Features:**
- Local LLM support via Ollama integration with automatic model management
- Redis-based caching with in-memory fallback and performance metrics
- Comprehensive error handling with circuit breaker pattern and automatic retries
- Advanced correction styles (6 options: Standard, Formal, Casual, Business, Error Focus, Concise)
- Mobile-responsive design with touch optimization and multiple breakpoints
- Batch processing API for multiple correction requests
- Admin monitoring endpoints for health checks and cache management
- Asynchronous operations for improved performance

## Critical Architecture Patterns

### Error Handling Strategy
All AI service calls go through ErrorHandler with:
- Exponential backoff retry (max 3 attempts)
- Circuit breaker pattern (opens after 5 failures in 5 minutes)
- Automatic fallback chain: Primary → OpenAI → Claude → Local LLM
- Service health monitoring and manual recovery endpoints

### Caching Strategy  
Two-tier caching system:
- Primary: Redis with 1-hour TTL for correction results
- Fallback: In-memory cache (last 100 entries) when Redis unavailable
- Cache keys include text + model + correction_style for proper invalidation
- Performance metrics tracked for cache hit/miss ratios

### Mobile-First Responsive Design
Three breakpoints with specific optimizations:
- Desktop (>768px): Full feature set with hover states
- Tablet (481-768px): Condensed layout with touch targets
- Mobile (≤480px): Bottom-sheet modals, stacked inputs, 44px minimum touch targets

**Architecture Notes:**
- Uses uv for Python dependency management with Ollama and Redis dependencies
- Frontend proxy configuration routes `/api/*` to backend with batch processing support
- Factory pattern supports three AI providers with automatic failover
- Database operations are async with proper connection handling
- Japanese-specific prompt engineering optimized for all three AI model types
- Circuit breaker state persists across application restarts for reliability