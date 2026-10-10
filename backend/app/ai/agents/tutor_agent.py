# ============================================
# NEXORA AI - Tutor Agent
# ============================================
# Educational AI agent।
# Complex topics সহজ করে শেখায়।

from typing import Dict, Optional
from app.ai.llm.router import llm_router
from app.core.logger import logger

# Tutor agent system prompt
TUTOR_SYSTEM_PROMPT = """You are NEXORA Tutor, an expert educational AI assistant.

Your teaching approach:
1. Break complex topics into simple parts
2. Use real-world examples and analogies  
3. Explain step-by-step when needed
4. Summarize key points clearly
5. Suggest what to learn next

Always be encouraging, patient, and clear.
Support both English and Bengali languages."""


class TutorAgent:
    """
    Educational AI Agent।
    Learning ও teaching এর জন্য specialized।
    """

    def __init__(self):
        self.name = "Tutor Agent"
        self.description = "Expert educational assistant for learning"

    async def teach(
        self,
        topic: str,
        difficulty_level: str = "intermediate",
        user_background: Optional[str] = None,
    ) -> Dict:
        """
        কোনো topic শেখানোর জন্য।
        
        Parameters:
            topic: কী শিখতে চায়
            difficulty_level: beginner/intermediate/advanced
            user_background: User এর আগের knowledge
        """
        # Context-aware prompt তৈরি
        prompt = f"""Please teach me about: {topic}

Difficulty Level: {difficulty_level}
{f'My background: {user_background}' if user_background else ''}

Structure your response as:
1. **Overview** (2-3 sentences)
2. **Core Concepts** (explain each clearly)
3. **Example** (practical illustration)
4. **Key Takeaways** (bullet points)
5. **What to Learn Next**"""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=TUTOR_SYSTEM_PROMPT,
            temperature=0.6,
            max_tokens=700,
        )

        return {
            "agent": "tutor",
            "topic": topic,
            "content": result["content"],
            "provider": result["provider"],
            "difficulty": difficulty_level,
        }

    async def explain(self, concept: str, context: Optional[str] = None) -> Dict:
        """
        একটি নির্দিষ্ট concept explain করে।
        """
        prompt = f"""Explain this concept clearly: {concept}
{f'Context: {context}' if context else ''}

Be concise but comprehensive. Use examples."""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=TUTOR_SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=500,
        )

        return {
            "agent": "tutor",
            "concept": concept,
            "content": result["content"],
            "provider": result["provider"],
        }

    async def quiz(self, topic: str, num_questions: int = 3) -> Dict:
        """
        Topic এর উপর quiz questions তৈরি করে।
        """
        prompt = f"""Create {num_questions} quiz questions about: {topic}

Format each question as:
Q: [Question]
A) [Option 1]
B) [Option 2]  
C) [Option 3]
D) [Option 4]
Answer: [Correct option]
Explanation: [Why this is correct]"""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=TUTOR_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=600,
        )

        return {
            "agent": "tutor",
            "topic": topic,
            "quiz": result["content"],
            "provider": result["provider"],
        }


# Singleton instance
tutor_agent = TutorAgent()
