# ============================================
# NEXORA AI - Cloud AI Service (Fallback)
# ============================================
# Ollama unavailable হলে Cloud AI ব্যবহার হয়।
# OpenAI GPT বা Anthropic Claude API।

import httpx
from typing import Optional, AsyncGenerator
from app.core.config import settings
from app.core.logger import logger


class CloudAIService:
    """
    Cloud AI service - OpenAI API wrapper।
    Ollama না চললে fallback হিসেবে কাজ করে।
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"          # Cheapest & fast model

    async def is_available(self) -> bool:
        """Cloud AI available কিনা check করে।"""
        return bool(self.api_key and self.api_key != "your-openai-key-here")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        OpenAI API দিয়ে response generate করে।
        """
        if not await self.is_available():
            return "Cloud AI configured নেই। Ollama চালু করুন।"

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status_code}")
                    return "Cloud AI response পেতে সমস্যা হয়েছে।"

        except Exception as e:
            logger.error(f"Cloud AI error: {e}")
            return f"Cloud AI Error: {str(e)}"

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        """OpenAI streaming response।"""
        # Simplified - non-streaming fallback
        response = await self.generate(prompt, system_prompt, temperature, max_tokens)
        # Word by word yield করা streaming simulate করতে
        for word in response.split():
            yield word + " "


# Singleton instance
cloud_service = CloudAIService()
