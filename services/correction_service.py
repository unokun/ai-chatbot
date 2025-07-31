from typing import List
from .openai_service import OpenAIService, CorrectionVariant
from database.models import CorrectionHistory, get_db
from sqlalchemy.orm import Session

class CorrectionService:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def correct_text(self, text: str, user_id: str = "anonymous") -> List[CorrectionVariant]:
        if not text.strip():
            return [CorrectionVariant(
                text=text,
                type="error", 
                reason="空のテキストは添削できません"
            )]
        
        variants = await self.openai_service.correct_japanese_text(text)
        
        self._save_correction_history(text, variants, user_id)
        
        return variants
    
    def _save_correction_history(self, original_text: str, variants: List[CorrectionVariant], user_id: str):
        try:
            db = next(get_db())
            
            for variant in variants:
                if variant.type != "error":
                    history = CorrectionHistory(
                        user_id=user_id,
                        original_text=original_text,
                        corrected_text=variant.text,
                        correction_type=variant.type,
                        ai_model_used="openai-gpt4o"
                    )
                    db.add(history)
            
            db.commit()
        except Exception as e:
            print(f"History save error: {e}")
        finally:
            db.close()