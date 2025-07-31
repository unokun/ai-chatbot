# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered Japanese message correction application with a LINE-style chat interface. The Phase 1 MVP implements typo correction and honorific/business language enhancement using OpenAI GPT-4o API integration.

## Development Commands

### Environment Setup
- `cp .env.example .env` - Copy environment template (requires OPENAI_API_KEY)
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

### Backend Structure (Python FastAPI)
- **main.py**: FastAPI application with CORS, API endpoints, and startup database initialization
- **services/correction_service.py**: Main correction logic coordinator
- **services/openai_service.py**: OpenAI GPT-4o integration with Japanese correction prompts
- **database/models.py**: SQLAlchemy models for correction_history and user_settings tables

### Frontend Structure (React + TypeScript)
- **src/App.tsx**: Main application component
- **src/components/ChatInterface.tsx**: Main chat container with message state management
- **src/components/MessageInput.tsx**: Input field with correction button and UNDO functionality
- **src/components/CorrectionModal.tsx**: Modal displaying 3 AI-generated correction variants
- **src/components/ChatMessages.tsx**: LINE-style message display component
- **src/services/api.ts**: Axios-based API client for backend communication

### Key API Flow
1. User inputs Japanese text in MessageInput
2. "添削" (correction) button triggers CorrectionModal
3. Modal calls `/api/correct` endpoint with text payload
4. Backend processes through OpenAI service with specialized Japanese prompts
5. Returns 3 variants: polite, casual, and corrected (with typo fixes + honorifics)
6. User selects variant, which updates input field with UNDO history tracking

### Database Schema
- **correction_history**: Stores original/corrected text pairs with AI model metadata
- **user_settings**: User preferences for AI model and correction style
- Auto-creates SQLite database on startup via FastAPI event handler

## Technology Stack

- **Frontend**: React + TypeScript + Vite + Axios + Lucide React icons
- **Backend**: Python FastAPI + SQLAlchemy + OpenAI SDK + python-dotenv
- **Database**: SQLite with automatic table creation
- **Dependency Management**: uv for Python, npm for Node.js

## Current Implementation Status (Phase 1 MVP)

✅ **Completed Features:**
- LINE-style chat UI with message bubbles
- Japanese text correction via OpenAI GPT-4o
- 3-variant correction display (polite/casual/corrected)
- UNDO functionality with history tracking
- SQLite persistence for correction history
- CORS-enabled API with automatic database initialization

**Architecture Notes:**
- Uses uv for Python dependency management instead of pip/poetry
- Frontend proxy configuration in vite.config.ts routes `/api/*` to backend
- Circular import prevention: CorrectionVariant model defined in openai_service.py
- Database session management with dependency injection pattern
- Japanese-specific OpenAI prompt engineering for business context