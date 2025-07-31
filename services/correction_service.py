from typing import List, Optional, Dict
from .openai_service import CorrectionVariant
from .ai_model_factory import AIModelFactory
from .cache_service import CacheService
from .error_handler import error_handler
from database.models import CorrectionHistory, UserSettings, get_db
from sqlalchemy.orm import Session
import logging
import time
import asyncio

logger = logging.getLogger(__name__)

class CorrectionService:
    def __init__(self):
        self.ai_factory = AIModelFactory()
        self.cache_service = CacheService()
        self.batch_requests = []
        self.batch_timeout = 0.5  # 500ms batch window
    
    async def correct_text(
        self, 
        text: str, 
        user_id: str = "anonymous", 
        preferred_model: Optional[str] = None,
        correction_style: str = "default",
        use_cache: bool = True
    ) -> List[CorrectionVariant]:
        if not text.strip():
            return [CorrectionVariant(
                text=text,
                type="error",
                reason="空のテキストは添削できません"
            )]
        
        # Get user's preferred model or use default
        model_name = preferred_model or self._get_user_preferred_model(user_id)
        
        # Check cache first
        if use_cache:
            cached_variants = await self.cache_service.get_cached_correction(text, model_name, correction_style)
            if cached_variants:
                logger.info(f"Cache hit for text: {text[:50]}...")
                return cached_variants
        
        # Get AI service instance with fallback logic
        ai_service, actual_model = await self._get_ai_service_with_fallback(model_name)
        if not ai_service:
            return [CorrectionVariant(
                text=text,
                type="error",
                reason="利用可能なAIモデルがありません"
            )]
        
        # Record start time for performance monitoring
        start_time = time.time()
        
        try:
            # Use error handler with retry logic
            variants = await error_handler.retry_with_backoff(
                ai_service.correct_japanese_text,
                text,
                max_retries=2
            )
            
            # Add performance info to variants
            processing_time = time.time() - start_time
            for variant in variants:
                variant.reason += f" (処理時間: {processing_time:.2f}秒)"
            
            # Cache the results
            if use_cache and variants:
                await self.cache_service.cache_correction(text, actual_model, variants, correction_style)
            
            # Save to history asynchronously
            asyncio.create_task(self._save_correction_history_async(text, variants, user_id, actual_model))
            
            return variants
            
        except Exception as e:
            logger.error(f"Correction error: {str(e)}")
            # Use error handler for comprehensive fallback
            fallback_models = ["openai-gpt4o", "claude-3-sonnet", "local-llm"]
            if actual_model in fallback_models:
                fallback_models.remove(actual_model)
            
            return await error_handler.handle_ai_service_error(
                actual_model, 
                e, 
                text, 
                fallback_models
            )
    
    def _get_user_preferred_model(self, user_id: str) -> str:
        """Get user's preferred AI model from database"""
        try:
            db = next(get_db())
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if user_settings and user_settings.preferred_ai_model:
                return user_settings.preferred_ai_model
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
        finally:
            db.close()
        
        return "openai-gpt4o"  # Default model
    
    def _save_correction_history(self, original_text: str, variants: List[CorrectionVariant], user_id: str, model_name: str):
        try:
            db = next(get_db())
            
            for variant in variants:
                if variant.type != "error":
                    history = CorrectionHistory(
                        user_id=user_id,
                        original_text=original_text,
                        corrected_text=variant.text,
                        correction_type=variant.type,
                        ai_model_used=model_name
                    )
                    db.add(history)
            
            db.commit()
        except Exception as e:
            logger.error(f"History save error: {e}")
        finally:
            db.close()
    
    def get_available_models(self) -> Dict[str, str]:
        """Get available AI models"""
        logger.info(f"ai_factory: {self.ai_factory}...")

        return self.ai_factory.get_available_models()
    
    async def set_user_preferred_model(self, user_id: str, model_name: str) -> bool:
        """Set user's preferred AI model"""
        if model_name not in self.ai_factory.get_available_models():
            return False
        
        try:
            db = next(get_db())
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            
            if user_settings:
                user_settings.preferred_ai_model = model_name
            else:
                user_settings = UserSettings(
                    user_id=user_id,
                    preferred_ai_model=model_name
                )
                db.add(user_settings)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting user preference: {e}")
            return False
        finally:
            db.close()
    
    async def _get_ai_service_with_fallback(self, model_name: str) -> tuple:
        """Get AI service with fallback logic"""
        ai_service = self.ai_factory.get_model(model_name)
        if ai_service:
            return ai_service, model_name
        
        # Try fallback models in order of preference
        fallback_models = ["openai-gpt4o", "claude-3-sonnet", "local-llm"]
        for fallback in fallback_models:
            if fallback != model_name:
                ai_service = self.ai_factory.get_model(fallback)
                if ai_service:
                    logger.warning(f"Model {model_name} not available, using {fallback}")
                    return ai_service, fallback
        
        return None, None
    
    async def _save_correction_history_async(self, original_text: str, variants: List[CorrectionVariant], user_id: str, model_name: str):
        """Asynchronously save correction history"""
        try:
            await asyncio.to_thread(self._save_correction_history, original_text, variants, user_id, model_name)
        except Exception as e:
            logger.error(f"Async history save error: {e}")
    
    async def correct_text_batch(self, requests: List[Dict]) -> List[List[CorrectionVariant]]:
        """Process multiple correction requests in batch"""
        tasks = []
        for req in requests:
            task = self.correct_text(
                text=req.get('text', ''),
                user_id=req.get('user_id', 'anonymous'),
                preferred_model=req.get('preferred_model'),
                correction_style=req.get('correction_style', 'default'),
                use_cache=req.get('use_cache', True)
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        return await self.cache_service.get_cache_stats()
    
    async def clear_cache(self) -> bool:
        """Clear correction cache"""
        return await self.cache_service.invalidate_cache()
    
    def get_service_health(self) -> Dict:
        """Get health status of all AI services"""
        return error_handler.get_service_health()
    
    def reset_service_circuit_breaker(self, service_name: str) -> bool:
        """Reset circuit breaker for a specific service"""
        try:
            error_handler.reset_circuit_breaker(service_name)
            return True
        except Exception as e:
            logger.error(f"Failed to reset circuit breaker for {service_name}: {str(e)}")
            return False