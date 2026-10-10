# ============================================
# NEXORA AI - Smart LLM Router
# ============================================
# Ollama available হলে local, না হলে cloud।
# Automatic failover with smart routing।

from typing import Optional, AsyncGenerator
from app.ai.llm.ollama_service import ollama_service
from app.ai.llm.cloud_service import cloud_service
from app.core.config import settings
from app.core.logger import logger


class LLMRouter:
    """
    Intelligent LLM routing।
    Priority: Local Ollama > Cloud AI > Error message
    
    ব্যবহার:
    - Ollama চালু থাকলে → Ollama ব্যবহার করে (free, private)
    - Ollama বন্ধ থাকলে → Cloud AI fallback (needs API key)
    """

    async def get_active_provider(self) -> str:
        """কোন AI provider ব্যবহার হচ্ছে তা জানায়।"""
        if await ollama_service.is_available():
            return "ollama"
        elif settings.USE_CLOUD_FALLBACK and await cloud_service.is_available():
            return "cloud"
        return "none"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict:
        """
        Smart routing দিয়ে response generate করে।
        Returns: {"content": str, "provider": str, "model": str}
        """
        provider = await self.get_active_provider()

        logger.info(f"🤖 Using AI provider: {provider}")

        if provider == "ollama":
            content = await ollama_service.generate(
                prompt, system_prompt, temperature, max_tokens
            )
            return {
                "content": content,
                "provider": "ollama",
                "model": settings.OLLAMA_MODEL
            }

        elif provider == "cloud":
            content = await cloud_service.generate(
                prompt, system_prompt, temperature, max_tokens
            )
            return {
                "content": content,
                "provider": "cloud",
                "model": "gpt-3.5-turbo"
            }

        else:
            # কোনো AI provider available নেই
            logger.warning("⚠️ No AI provider available")
            return {
                "content": "AI service unavailable। Ollama চালু করুন: 'ollama serve'",
                "provider": "none",
                "model": "none"
            }

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming response router।
        """
        provider = await self.get_active_provider()

        if provider == "ollama":
            async for token in ollama_service.generate_stream(
                prompt, system_prompt, temperature, max_tokens
            ):
                yield token

        elif provider == "cloud":
            async for token in cloud_service.generate_stream(
                prompt, system_prompt, temperature, max_tokens
            ):
                yield token

        else:
            yield "AI service unavailable। Ollama চালু করুন।"

    async def get_status(self) -> dict:
        """
        সব AI provider এর status।
        Dashboard এ দেখানোর জন্য।
        """
        ollama_available = await ollama_service.is_available()
        cloud_available = await cloud_service.is_available()

        models = []
        if ollama_available:
            models = await ollama_service.get_available_models()

        return {
            "ollama": {
                "available": ollama_available,
                "models": models,
                "current_model": settings.OLLAMA_MODEL
            },
            "cloud": {
                "available": cloud_available,
                "provider": "OpenAI" if cloud_available else "Not configured"
            },
            "active_provider": await self.get_active_provider()
        }


# Singleton router instance
llm_router = LLMRouter()
