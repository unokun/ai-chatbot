from abc import ABC, abstractmethod
from typing import List
from .openai_service import CorrectionVariant

class BaseAIService(ABC):
    """Abstract base class for AI correction services"""
    
    @abstractmethod
    async def correct_japanese_text(self, text: str) -> List[CorrectionVariant]:
        """Correct Japanese text and return correction variants"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name identifier"""
        pass