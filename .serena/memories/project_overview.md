# AI Message Correction App - Project Overview

## Purpose
An AI-powered Japanese message correction application with a LINE-style chat interface. The application supports multiple AI models (OpenAI GPT-4o, Claude 3 Sonnet, and Local LLMs via Ollama) for typo correction, honorific enhancement, and business language improvement with advanced features including caching, error handling, and mobile optimization.

## Current Status
Phase 3 Complete - All core features implemented including multi-AI support, local LLM integration, caching, error handling, and mobile-responsive design.

## Key Features
- LINE-style chat UI with message bubbles
- Japanese text correction with 3-variant display (polite, casual, corrected)  
- Multiple AI model support with user preferences
- Local LLM support via Ollama integration
- Redis-based caching with in-memory fallback
- Circuit breaker pattern with automatic failover
- Six correction styles (Standard, Formal, Casual, Business, Error Focus, Concise)
- Mobile-responsive design with touch optimization
- UNDO functionality with history tracking
- Batch processing API for multiple requests
- Admin monitoring endpoints

## Architecture
Multi-tier architecture with:
- **Frontend**: React + TypeScript SPA with Vite
- **Backend**: Python FastAPI with async operations  
- **Database**: SQLite with SQLAlchemy ORM
- **Caching**: Redis with in-memory fallback
- **AI Services**: Factory pattern supporting OpenAI, Claude, and Local LLMs
- **Error Handling**: Circuit breaker with exponential backoff retry logic