import os
from openai import AsyncOpenAI
from typing import List
from pydantic import BaseModel
import logging
from .base_ai_service import BaseAIService
from .correction_variant import CorrectionVariant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class OpenAIService(BaseAIService):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = AsyncOpenAI(api_key=api_key)
    
    async def correct_japanese_text(self, text: str) -> List[CorrectionVariant]:
        system_prompt = """
あなたは日本語ビジネス文書の添削専門家です。以下の文章を3つの方向性で添削してください：

1. 丁寧な表現版: より敬語を使った丁寧な表現に変換
2. カジュアル表現版: 親しみやすい表現に変換（ただしビジネス適切範囲内）
3. 誤字修正+敬語版: 誤字脱字を修正し、適切な敬語表現に変換

それぞれについて：
- 修正後のテキスト
- 修正タイプ（polite/casual/corrected）
- 修正理由を簡潔に説明

JSON形式で回答してください：
{
  "variants": [
    {"text": "修正後テキスト", "type": "polite", "reason": "修正理由"},
    {"text": "修正後テキスト", "type": "casual", "reason": "修正理由"},
    {"text": "修正後テキスト", "type": "corrected", "reason": "修正理由"}
  ]
}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下の文章を添削してください：\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=10000
            )
            content = response.choices[0].message.content
            logging.info(f"Response: {content}")
            # print(f"Content repr: {repr(content)}")

            import json
            result = json.loads(content)
            
            variants = []
            for variant_data in result["variants"]:
                variants.append(CorrectionVariant(
                    text=variant_data["text"],
                    type=variant_data["type"],
                    reason=variant_data["reason"]
                ))
            
            return variants
            
        except Exception as e:
            return [
                CorrectionVariant(
                    text=text,
                    type="error",
                    reason=f"AI処理エラー: {str(e)}"
                )
            ]
    
    @property
    def model_name(self) -> str:
        return "openai-gpt4o"