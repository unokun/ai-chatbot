# Task Completion Checklist

## Before Committing Changes

### Code Validation
1. **Backend Syntax Check**:
   ```bash
   python -m py_compile main.py
   python -m py_compile services/*.py
   ```

2. **Frontend TypeScript Validation**:
   ```bash
   npm run build
   ```

### Testing Workflow
⚠️ **No formal test suite currently configured**
- Manual testing via API endpoints recommended
- Use FastAPI docs interface: http://localhost:8000/docs
- Test correction functionality via frontend: http://localhost:5173

### Service Health Verification
```bash
# Check all AI services status
curl http://localhost:8000/api/admin/health

# Verify cache is working
curl http://localhost:8000/api/admin/cache-stats
```

## Deployment Checklist

### Environment Variables Required
- `OPENAI_API_KEY` - For OpenAI GPT-4o integration
- `ANTHROPIC_API_KEY` - For Claude 3 Sonnet integration
- Redis connection (optional, falls back to in-memory cache)

### Service Dependencies
- Ollama service running (for local LLM support)
- Redis server (optional but recommended)
- SQLite database (auto-created)

## Code Quality Standards

### Before Pull Requests
1. Follow established code style conventions
2. Add appropriate error handling with logging
3. Update docstrings for new methods/classes
4. Ensure mobile responsiveness for frontend changes
5. Test fallback mechanisms for AI service changes

### Performance Considerations
- Use async/await for I/O operations
- Implement proper caching strategies
- Monitor circuit breaker behavior for service reliability
- Optimize bundle size for frontend changes

## Documentation Updates
- Update CLAUDE.md if adding new features
- Consider updating README.md for significant changes
- Add API endpoint documentation for new endpoints