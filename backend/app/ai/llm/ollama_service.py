# ============================================
# NEXORA AI - Ollama Local LLM Service
# ============================================
# Ollama দিয়ে local AI model (TinyLlama/Phi3)
# চালানো হয়। Streaming support সহ।

import httpx
import json
from typing import AsyncGenerator, Optional
from app.core.config import settings
from app.core.logger import logger


class OllamaService:
    """
    Ollama API wrapper class।
    Local LLM এর সাথে সব communication এখান দিয়ে হয়।
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def is_available(self) -> bool:
        """
        Ollama server চালু আছে কিনা check করে।
        Health check এ ব্যবহার হয়।
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def get_available_models(self) -> list:
        """
        Ollama তে install করা models এর list পায়।
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
        return []

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        একটি সম্পূর্ণ response generate করে।
        Streaming ছাড়া - পুরো response একসাথে পায়।
        """
        try:
            messages = []

            # System prompt থাকলে add করা
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 2048,          # Context window size
                }
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["message"]["content"]
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return "দুঃখিত, AI response generate করতে সমস্যা হয়েছে।"

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            return "Response সময়সীমা শেষ হয়েছে। আবার চেষ্টা করুন।"
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            return f"Error: {str(e)}"

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming response generator।
        Token by token response পাঠায় - real-time typing effect।
        FastAPI StreamingResponse এর সাথে ব্যবহার হয়।
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,                # Streaming চালু
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 2048,
                }
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if not data.get("done", False):
                                    token = data.get("message", {}).get("content", "")
                                    if token:
                                        yield token
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield f"Error: {str(e)}"


# Singleton instance
ollama_service = OllamaService()
