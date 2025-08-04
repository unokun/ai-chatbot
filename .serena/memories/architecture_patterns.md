# Architecture Patterns & Design Guidelines

## Core Design Patterns

### 1. Factory Pattern (AI Services)
- **Implementation**: `AIModelFactory` manages all AI service instances
- **Benefits**: Lazy loading, centralized model management, easy extensibility
- **Usage**: `AIModelFactory.get_model(model_name)` returns service instance

### 2. Abstract Base Class Pattern
- **Implementation**: `BaseAIService` defines interface for all AI providers
- **Required Methods**: `correct_japanese_text()`, `model_name` property
- **Benefits**: Consistent interface, enforced implementation contracts

### 3. Circuit Breaker Pattern
- **Implementation**: `ErrorHandler` class with automatic failover
- **Behavior**: Opens after 5 failures in 5 minutes, provides fallback chains
- **Monitoring**: Service health endpoints for observability

### 4. Two-Tier Caching Strategy
- **Primary**: Redis with 1-hour TTL for correction results
- **Fallback**: In-memory cache (last 100 entries) when Redis unavailable
- **Key Strategy**: `text + model + correction_style` for cache invalidation

## Error Handling Philosophy

### Graceful Degradation
1. **Retry Logic**: Exponential backoff (max 3 attempts)
2. **Service Fallback**: Primary → OpenAI → Claude → Local LLM
3. **Cache Fallback**: Redis → In-memory → Fresh computation
4. **UI Fallback**: Error variants with helpful messages

### Async Operation Patterns
```python
# Preferred async pattern
async def async_operation():
    try:
        result = await some_io_operation()
        return result
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        raise
```

## Mobile-First Responsive Design

### Breakpoint Strategy
- **Mobile**: ≤480px (bottom-sheet modals, stacked inputs)
- **Tablet**: 481-768px (condensed layout, touch targets)  
- **Desktop**: >768px (full feature set, hover states)

### Touch Optimization
- Minimum 44px touch targets
- Optimized modal presentations
- Swipe-friendly interfaces

## Database Design Principles

### Schema Patterns
- **User Settings**: Flexible JSON storage for preferences
- **History Tracking**: Denormalized for query performance
- **Indexes**: Strategic placement on user_id and timestamps

### Connection Management
- Async SQLAlchemy operations
- Proper connection cleanup in finally blocks
- Database auto-creation on startup

## API Design Conventions

### Endpoint Organization
```
/api/correct          # Core functionality
/api/models           # Model management
/api/user/*           # User-specific operations
/api/admin/*          # Administrative endpoints
```

### Request/Response Patterns
- Pydantic models for validation
- Consistent error response format
- Optional parameters with sensible defaults

## Performance Optimization

### Async Concurrency
- Batch processing for multiple requests
- Non-blocking I/O for database operations
- Background tasks for history saving

### Caching Strategy
- Cache keys include all relevant parameters
- TTL management for data freshness
- Performance metrics tracking