import logging
import traceback
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from .openai_service import CorrectionVariant

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self.max_retries = 3
        self.retry_delay = 1.0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        
    async def handle_ai_service_error(
        self, 
        service_name: str, 
        error: Exception, 
        text: str,
        fallback_services: List[str] = None
    ) -> List[CorrectionVariant]:
        """Handle AI service errors with fallback and circuit breaker logic"""
        
        # Log the error
        logger.error(f"AI service error in {service_name}: {str(error)}")
        
        # Update error tracking
        self._update_error_tracking(service_name, error)
        
        # Check if service is in circuit breaker state
        if self._is_circuit_breaker_open(service_name):
            logger.warning(f"Circuit breaker open for {service_name}")
            return await self._try_fallback_services(text, fallback_services or [])
        
        # Try fallback services
        if fallback_services:
            for fallback_service in fallback_services:
                if not self._is_circuit_breaker_open(fallback_service):
                    try:
                        from .ai_model_factory import AIModelFactory
                        fallback_ai = AIModelFactory.get_model(fallback_service)
                        if fallback_ai:
                            logger.info(f"Trying fallback service: {fallback_service}")
                            variants = await fallback_ai.correct_japanese_text(text)
                            # Add fallback notification to variants
                            for variant in variants:
                                variant.reason += f" (フォールバック: {service_name} → {fallback_service})"
                            return variants
                    except Exception as fallback_error:
                        logger.error(f"Fallback service {fallback_service} also failed: {str(fallback_error)}")
                        self._update_error_tracking(fallback_service, fallback_error)
                        continue
        
        # Return error variants if all services fail
        return [
            CorrectionVariant(
                text=text,
                type="error",
                reason=f"すべてのAIサービスでエラーが発生しました: {str(error)}"
            )
        ]
    
    async def retry_with_backoff(
        self, 
        func, 
        *args, 
        max_retries: Optional[int] = None,
        base_delay: float = 1.0,
        **kwargs
    ):
        """Retry function with exponential backoff"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    def _update_error_tracking(self, service_name: str, error: Exception):
        """Update error tracking for circuit breaker logic"""
        now = datetime.now()
        
        # Initialize tracking for service if not exists
        if service_name not in self.error_counts:
            self.error_counts[service_name] = []
        
        # Add error with timestamp
        self.error_counts[service_name].append({
            'timestamp': now,
            'error': str(error),
            'type': type(error).__name__
        })
        
        # Clean old errors (older than circuit breaker timeout)
        cutoff_time = now - timedelta(seconds=self.circuit_breaker_timeout)
        self.error_counts[service_name] = [
            err for err in self.error_counts[service_name] 
            if err['timestamp'] > cutoff_time
        ]
        
        self.last_errors[service_name] = {
            'timestamp': now,
            'error': str(error),
            'type': type(error).__name__
        }
    
    def _is_circuit_breaker_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open for a service"""
        if service_name not in self.error_counts:
            return False
        
        recent_errors = self.error_counts[service_name]
        return len(recent_errors) >= self.circuit_breaker_threshold
    
    async def _try_fallback_services(self, text: str, fallback_services: List[str]) -> List[CorrectionVariant]:
        """Try fallback services in order"""
        for service_name in fallback_services:
            if not self._is_circuit_breaker_open(service_name):
                try:
                    from .ai_model_factory import AIModelFactory
                    service = AIModelFactory.get_model(service_name)
                    if service:
                        variants = await service.correct_japanese_text(text)
                        for variant in variants:
                            variant.reason += f" (フォールバック利用)"
                        return variants
                except Exception as e:
                    logger.error(f"Fallback service {service_name} failed: {str(e)}")
                    self._update_error_tracking(service_name, e)
                    continue
        
        # All fallback services failed
        return [
            CorrectionVariant(
                text=text,
                type="error",
                reason="すべてのフォールバックサービスが利用できません"
            )
        ]
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all services"""
        health_status = {}
        
        for service_name in ['openai-gpt4o', 'claude-3-sonnet', 'local-llm']:
            recent_errors = self.error_counts.get(service_name, [])
            is_circuit_open = self._is_circuit_breaker_open(service_name)
            last_error = self.last_errors.get(service_name)
            
            health_status[service_name] = {
                'status': 'down' if is_circuit_open else 'up',
                'recent_error_count': len(recent_errors),
                'circuit_breaker_open': is_circuit_open,
                'last_error': last_error,
                'next_retry_available': not is_circuit_open
            }
        
        return health_status
    
    def reset_circuit_breaker(self, service_name: str):
        """Manually reset circuit breaker for a service"""
        if service_name in self.error_counts:
            self.error_counts[service_name] = []
        if service_name in self.last_errors:
            del self.last_errors[service_name]
        logger.info(f"Circuit breaker reset for {service_name}")

# Global error handler instance
error_handler = ErrorHandler()