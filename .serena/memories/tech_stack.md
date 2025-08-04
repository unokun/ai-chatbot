# Technology Stack

## Frontend
- **Framework**: React 19.1.1 + TypeScript
- **Build Tool**: Vite 4.5.3 with HMR
- **HTTP Client**: Axios 1.5.0
- **Icons**: Lucide React 0.534.0
- **Styling**: CSS modules with mobile-first responsive design

## Backend  
- **Framework**: Python FastAPI with async/await
- **Python Version**: >=3.11
- **Dependencies**:
  - `anthropic>=0.28.0` - Claude API client
  - `openai>=1.97.1` - OpenAI API client  
  - `ollama>=0.3.2` - Local LLM integration
  - `redis>=5.1.1` - Caching layer
  - `sqlalchemy>=2.0.42` - Database ORM
  - `uvicorn>=0.35.0` - ASGI server
  - `pydantic>=2.11.7` - Data validation
  - `python-dotenv>=1.1.1` - Environment management

## Database & Storage
- **Primary Database**: SQLite with SQLAlchemy async ORM
- **Caching**: Redis (primary) with in-memory fallback
- **Environment**: .env file configuration

## AI Models
- **OpenAI**: GPT-4o for high-quality corrections
- **Claude**: Claude 3 Sonnet for alternative processing
- **Local LLMs**: Ollama integration supporting:
  - Qwen2.5:3b-instruct (preferred)
  - Llama3.2:latest  
  - Gemma2:2b-instruct

## Development Tools
- **Package Management**: uv for Python, npm for Node.js
- **Development Server**: Concurrently for parallel dev/backend
- **Module System**: ES modules (Node.js type: "module")