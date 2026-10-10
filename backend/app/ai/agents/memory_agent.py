# ============================================
# NEXORA AI - Memory Agent
# ============================================
# Conversation memory management।
# Chat history থেকে context maintain করে।

from typing import Dict, List, Optional
from app.ai.llm.router import llm_router
from app.core.logger import logger


class MemoryAgent:
    """
    Conversation Memory Agent।
    Chat history সংগ্রহ করে এবং context তৈরি করে।
    """

    def __init__(self, max_history: int = 10):
        """
        max_history: কতটি পুরনো message memory তে রাখবে।
        বেশি রাখলে context ভালো, কিন্তু tokens বেশি লাগে।
        """
        self.max_history = max_history

    def build_context_from_history(
        self,
        messages: List[Dict],
        max_tokens: int = 1000
    ) -> str:
        """
        Chat history থেকে LLM এর জন্য context string তৈরি করে।
        
        Parameters:
            messages: [{"role": "user/assistant", "content": "..."}]
            max_tokens: Context এর approximate maximum length
        
        Returns:
            Formatted conversation history string
        """
        if not messages:
            return ""

        # শুধু শেষ N messages নেওয়া
        recent_messages = messages[-self.max_history:]

        context_parts = ["## Previous Conversation:"]

        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Content truncate করা (বেশি লম্বা হলে)
            if len(content) > 300:
                content = content[:300] + "..."

            if role == "user":
                context_parts.append(f"Human: {content}")
            elif role == "assistant":
                context_parts.append(f"NEXORA: {content}")

        return "\n".join(context_parts)

    async def generate_with_memory(
        self,
        current_message: str,
        chat_history: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """
        Chat history কে context হিসেবে ব্যবহার করে response তৈরি।
        
        এটাই Conversation Memory এর মূল কাজ।
        পুরনো conversation মনে রেখে relevant উত্তর দেয়।
        """
        # History থেকে context তৈরি করা
        history_context = self.build_context_from_history(chat_history)

        # System prompt + history + current message একত্রিত করা
        if history_context:
            full_prompt = f"""{history_context}

## Current Question:
Human: {current_message}

NEXORA:"""
        else:
            full_prompt = current_message

        # LLM দিয়ে response generate করা
        result = await llm_router.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500,
        )

        return {
            "agent": "memory",
            "content": result["content"],
            "provider": result["provider"],
            "history_used": len(chat_history),
        }

    async def summarize_conversation(self, messages: List[Dict]) -> Dict:
        """
        Long conversation কে summarize করে।
        Memory optimization এর জন্য।
        """
        if len(messages) < 5:
            return {"summary": "Conversation too short to summarize", "provider": "none"}

        # Conversation text তৈরি করা
        conversation_text = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "AI"
            conversation_text.append(f"{role}: {msg['content']}")

        full_conversation = "\n".join(conversation_text)

        prompt = f"""Summarize this conversation in 3-5 key points:

{full_conversation[:2000]}

Summary:"""

        result = await llm_router.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=300,
        )

        return {
            "summary": result["content"],
            "provider": result["provider"],
            "messages_summarized": len(messages),
        }

    def extract_key_info(self, messages: List[Dict]) -> Dict:
        """
        Conversation থেকে important information extract করে।
        User preferences, mentioned names, topics ইত্যাদি।
        """
        topics_mentioned = []
        questions_asked = []

        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # Questions identify করা
                if "?" in content:
                    questions_asked.append(content[:100])

        return {
            "total_messages": len(messages),
            "questions_asked": len(questions_asked),
            "recent_questions": questions_asked[-3:] if questions_asked else [],
        }


# Singleton instance
memory_agent = MemoryAgent(max_history=10)
