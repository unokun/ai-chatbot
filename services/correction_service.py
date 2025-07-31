from typing import List, Optional, Dict
from .openai_service import CorrectionVariant
from .ai_model_factory import AIModelFactory
from database.models import CorrectionHistory, UserSettings, get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class CorrectionService:
    def __init__(self):
        self.ai_factory = AIModelFactory()
    
    async def correct_text(self, text: str, user_id: str = "anonymous", preferred_model: Optional[str] = None) -> List[CorrectionVariant]:
        if not text.strip():
            return [CorrectionVariant(
                text=text,
                type="error", 
                reason="空のテキストは添削できません"
            )]
        
        # Get user's preferred model or use default
        model_name = preferred_model or self._get_user_preferred_model(user_id)
        
        # Get AI service instance
        ai_service = self.ai_factory.get_model(model_name)
        if not ai_service:
            # Fallback to OpenAI if preferred model is not available
            logger.warning(f"Model {model_name} not available, falling back to OpenAI")
            ai_service = self.ai_factory.get_model("openai-gpt4o")
            if not ai_service:
                return [CorrectionVariant(
                    text=text,
                    type="error",
                    reason="利用可能なAIモデルがありません"
                )]
            model_name = "openai-gpt4o"
        
        variants = await ai_service.correct_japanese_text(text)
        
        self._save_correction_history(text, variants, user_id, model_name)
        
        return variants
    
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