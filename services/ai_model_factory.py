from typing import Dict, Optional
from .base_ai_service import BaseAIService
from .openai_service import OpenAIService
from .claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class AIModelFactory:
    """Factory class for managing different AI models"""
    
    _models: Dict[str, BaseAIService] = {}
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """Get available AI models with their display names"""
        return {
            "openai-gpt4o": "OpenAI GPT-4o",
            "claude-3-sonnet": "Claude 3 Sonnet"
        }
    
    @classmethod
    def get_model(cls, model_name: str) -> Optional[BaseAIService]:
        """Get an AI service instance by model name"""
        if model_name not in cls._models:
            try:
                if model_name == "openai-gpt4o":
                    cls._models[model_name] = OpenAIService()
                elif model_name == "claude-3-sonnet":
                    cls._models[model_name] = ClaudeService()
                else:
                    logger.error(f"Unknown model: {model_name}")
                    return None
            except Exception as e:
                logger.error(f"Failed to initialize {model_name}: {str(e)}")
                return None
        
        return cls._models.get(model_name)
    
    @classmethod
    def is_model_available(cls, model_name: str) -> bool:
        """Check if a model is available and can be initialized"""
        try:
            model = cls.get_model(model_name)
            return model is not None
        except Exception:
            return False