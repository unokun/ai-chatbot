import os
import asyncio
from typing import List
import logging
from anthropic import AsyncAnthropic
from .openai_service import CorrectionVariant
from .base_ai_service import BaseAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeService(BaseAIService):
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = AsyncAnthropic(api_key=api_key)
    
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
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"以下の文章を添削してください：\n{text}"}
                ]
            )
            
            content = response.content[0].text
            logger.info(f"Claude response: {content}")
            
            import json
            # Extract JSON from response if it's wrapped in markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.rfind("```")
                content = content[start:end].strip()
            
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
            logger.error(f"Claude API error: {str(e)}")
            return [
                CorrectionVariant(
                    text=text,
                    type="error",
                    reason=f"Claude AI処理エラー: {str(e)}"
                )
            ]
    
    @property
    def model_name(self) -> str:
        return "claude-3-sonnet"