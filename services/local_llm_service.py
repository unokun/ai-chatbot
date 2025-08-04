import ollama
import asyncio
import logging
from typing import List, Optional
from .base_ai_service import BaseAIService
from .openai_service import CorrectionVariant

logger = logging.getLogger(__name__)

class LocalLLMService(BaseAIService):
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.local_model = model_name
        self._client = None
        
    @property
    def model_name(self) -> str:
        return f"local-{self.local_model}"
    
    def _get_client(self):
        if self._client is None:
            self._client = ollama.Client()
        return self._client
    
    async def correct_japanese_text(self, text: str) -> List[CorrectionVariant]:
        try:
            client = self._get_client()
            
            # Check if model is available locally
            available_models = await asyncio.to_thread(client.list)
            model_names = [model['model'] for model in available_models.get('models', [])]
            # Use a fallback model if the preferred one isn't available
            actual_model = self.local_model
            # logger.info(f"actual_model: {actual_model}")
            if self.local_model not in model_names:
                # Try common Japanese models
                fallback_models = ['qwen2.5:3b-instruct', 'llama3.2:latest', 'gemma2:2b-instruct']
                for fallback in fallback_models:
                    if fallback in model_names:
                        actual_model = fallback
                        break
                else:
                    # If no suitable model found, pull a lightweight one
                    logger.info(f"Pulling {self.local_model} model...")
                    await asyncio.to_thread(client.pull, 'qwen2.5:3b-instruct')
                    actual_model = 'qwen2.5:3b-instruct'
            
            # Create prompts for different correction styles
            prompts = [
                self._create_formal_prompt(text),
                self._create_casual_prompt(text),
                self._create_error_correction_prompt(text)
            ]
            
            variants = []
            
            for i, prompt in enumerate(prompts):
                try:
                    response = await asyncio.to_thread(
                        client.chat,
                        model=actual_model,
                        messages=[{'role': 'user', 'content': prompt}],
                        options={'temperature': 0.3, 'num_predict': 200}
                    )
                    
                    corrected_text = response['message']['content'].strip()
                    
                    # Extract just the corrected text if the model includes explanation
                    lines = corrected_text.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('理由') and not line.startswith('説明'):
                            corrected_text = line.strip()
                            break
                    
                    type = ["polite", "casual", "corrected"][i]
                    variant_type = ["丁寧な表現", "カジュアル表現", "誤字・文法修正"][i]
                    reason = f"ローカルLLM({actual_model})による{variant_type}"
                    
                    variants.append(CorrectionVariant(
                        text=corrected_text,
                        type=type,
                        reason=reason
                    ))
                    
                except Exception as e:
                    logger.error(f"Error generating variant {i+1}: {str(e)}")
                    # Fallback to original text with error message
                    variants.append(CorrectionVariant(
                        text=text,
                        reason=f"ローカルLLM処理エラー: {str(e)}"
                    ))
            
            return variants
            
        except Exception as e:
            logger.error(f"Local LLM service error: {str(e)}")
            # Return fallback variants
            return [
                CorrectionVariant(text=text, reason=f"ローカルLLMエラー: {str(e)}"),
                CorrectionVariant(text=text, reason="ローカルLLM利用不可"),
                CorrectionVariant(text=text, reason="オフライン処理失敗")
            ]
    
    def _create_formal_prompt(self, text: str) -> str:
        return f"""以下の日本語テキストを、ビジネスシーンに適した丁寧で正式な表現に修正してください。敬語を適切に使用し、フォーマルな文体にしてください。

原文: {text}

修正されたテキストのみを出力してください。説明は不要です。"""

    def _create_casual_prompt(self, text: str) -> str:
        return f"""以下の日本語テキストを、親しみやすくカジュアルな表現に修正してください。硬すぎる表現を柔らかくし、日常会話に適した文体にしてください。

原文: {text}

修正されたテキストのみを出力してください。説明は不要です。"""

    def _create_error_correction_prompt(self, text: str) -> str:
        return f"""以下の日本語テキストの誤字・脱字・文法エラーを修正してください。意味を変えずに、正しい日本語表現に直してください。

原文: {text}

修正されたテキストのみを出力してください。説明は不要です。"""
    
    async def is_available(self) -> bool:
        """Check if the local LLM service is available"""
        try:
            client = self._get_client()
            await asyncio.to_thread(client.list)
            return True
        except Exception as e:
            logger.error(f"Local LLM not available: {str(e)}")
            return False