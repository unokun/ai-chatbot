# Code Style & Conventions

## Python Backend Style

### Class & Method Conventions
- **Classes**: PascalCase (e.g., `CorrectionService`, `BaseAIService`)
- **Methods**: snake_case with descriptive names (e.g., `correct_japanese_text`, `_get_user_preferred_model`)
- **Private methods**: Prefix with underscore (e.g., `_update_error_tracking`)
- **Async methods**: Use `async def` for I/O operations

### Docstrings & Comments
- **Class docstrings**: Triple quotes with brief description
- **Method docstrings**: Describe purpose, parameters, and return values
- **Inline comments**: Explain complex logic, especially error handling

### Error Handling Pattern
- Comprehensive try/except blocks with specific error logging
- Circuit breaker pattern for service reliability
- Fallback mechanisms with graceful degradation
- Log errors with context using `logger.error(f"message: {str(e)}")`

### Data Models
- **Pydantic models**: For API request/response validation
- **SQLAlchemy models**: For database entities
- **Type hints**: Extensive use throughout codebase

## TypeScript Frontend Style

### Component Conventions
- **Components**: PascalCase functional components with TypeScript
- **Props interfaces**: Named `ComponentNameProps` (e.g., `MessageInputProps`)
- **State**: useState hooks with descriptive names
- **Event handlers**: Prefix with `handle` (e.g., `handleSend`, `handleCorrection`)

### Import Organization
```typescript
// External libraries first
import React, { useState } from 'react'
import { Send, Edit3 } from 'lucide-react'

// Local components
import CorrectionModal from './CorrectionModal'
import './ComponentName.css'
```

### Interface Definitions
- Optional props with default values in destructuring
- Explicit typing for event handlers (e.g., `React.KeyboardEvent`)

## File Organization

### Backend Structure
```
services/
├── base_ai_service.py        # Abstract base class
├── ai_model_factory.py       # Factory pattern implementation  
├── openai_service.py         # OpenAI integration
├── claude_service.py         # Claude integration
├── local_llm_service.py      # Ollama integration
├── correction_service.py     # Main orchestration
├── cache_service.py          # Redis + fallback caching
└── error_handler.py          # Circuit breaker + retry logic
```

### Frontend Structure
```
src/components/
├── ChatInterface.tsx         # Main container
├── MessageInput.tsx          # Input with correction triggers
├── CorrectionModal.tsx       # Correction results display
├── ModelSelector.tsx         # AI model selection
└── *.css                     # Component-specific styles
```

## Database Conventions
- **Table names**: snake_case (e.g., `correction_history`, `user_settings`)
- **Foreign keys**: Explicit naming with table references
- **Indexes**: On frequently queried columns (user_id, timestamps)