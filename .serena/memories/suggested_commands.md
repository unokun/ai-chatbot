# Essential Development Commands

## Environment Setup
```bash
# Copy environment template (requires OPENAI_API_KEY and ANTHROPIC_API_KEY)
cp .env.example .env

# Install Python dependencies using uv
uv sync

# Install Node.js dependencies  
npm install
```

## Development Servers
```bash
# Start both frontend and backend concurrently (RECOMMENDED)
npm run dev:all

# OR start individually:
npm run dev          # Frontend only (Vite dev server on port 5173)
npm run backend      # Backend only (FastAPI on port 8000)

# Alternative backend command
uv run uvicorn main:app --reload --port 8000

# Start ollama service (if using local LLMs)
ollama serve
```

## Build & Deploy
```bash
# Build frontend for production
npm run build

# Preview production build
npm run preview
```

## Validation Commands
```bash
# Check backend syntax
python -m py_compile main.py
python -m py_compile services/*.py

# Validate TypeScript compilation
npm run build
```

## API Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## Git Workflow
```bash
# Standard git operations (Linux environment)
git status
git add .
git commit -m "message"
git push
```

## System Commands (Linux WSL2)
```bash
# File operations
ls -la              # List files with details
find . -name "*.py" # Find Python files
grep -r "pattern"   # Search in files (prefer using tools)

# Process management
ps aux | grep uvicorn  # Check if backend is running
kill -9 <pid>         # Stop process if needed
```

## Project-Specific Commands
```bash
# Check if all services are healthy
curl http://localhost:8000/api/admin/health

# View cache statistics  
curl http://localhost:8000/api/admin/cache-stats

# Clear cache manually
curl -X POST http://localhost:8000/api/admin/clear-cache
```