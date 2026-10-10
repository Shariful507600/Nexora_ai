# ============================================
# NEXORA AI - Planner Agent
# ============================================
# Task planning ও productivity AI agent।
# Goals কে actionable steps এ ভাগ করে।

from typing import Dict, Optional, List
from app.ai.llm.router import llm_router
from app.core.logger import logger

PLANNER_SYSTEM_PROMPT = """You are NEXORA Planner, an expert productivity and planning AI.

Your capabilities:
1. Break down complex goals into actionable tasks
2. Create structured project plans with timelines
3. Prioritize tasks effectively (using Eisenhower Matrix)
4. Identify potential blockers and solutions
5. Suggest resources and tools needed

Always be practical, realistic, and organized.
Support both English and Bengali languages."""


class PlannerAgent:
    """
    Productivity ও Planning AI Agent।
    Goals থেকে actionable plans তৈরি করে।
    """

    def __init__(self):
        self.name = "Planner Agent"
        self.description = "Expert productivity and task planning assistant"

    async def create_plan(
        self,
        goal: str,
        timeframe: Optional[str] = None,
        constraints: Optional[str] = None,
    ) -> Dict:
        """
        একটি goal এর জন্য complete plan তৈরি করে।
        """
        prompt = f"""Create a detailed action plan for this goal:

**Goal:** {goal}
{f'**Timeframe:** {timeframe}' if timeframe else ''}
{f'**Constraints:** {constraints}' if constraints else ''}

Structure the plan as:
## Project Overview
[Brief description]

## Phase 1: Foundation (Week 1-2)
- Task 1: [Specific action]
- Task 2: [Specific action]

## Phase 2: Development (Week 3-4)
- Task 1: [Specific action]

## Phase 3: Completion
- Task 1: [Specific action]

## Success Metrics
[How to measure completion]

## Potential Challenges & Solutions
[List challenges with solutions]"""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=800,
        )

        return {
            "agent": "planner",
            "goal": goal,
            "plan": result["content"],
            "provider": result["provider"],
            "timeframe": timeframe,
        }

    async def prioritize_tasks(self, tasks: List[str]) -> Dict:
        """
        Tasks কে priority অনুযায়ী সাজায়।
        Eisenhower Matrix ব্যবহার করে।
        """
        tasks_text = "\n".join([f"- {task}" for task in tasks])

        prompt = f"""Prioritize these tasks using the Eisenhower Matrix:

**Tasks:**
{tasks_text}

Categorize as:
## 🔴 Do First (Urgent + Important)
## 🟡 Schedule (Important, Not Urgent)  
## 🔵 Delegate (Urgent, Not Important)
## ⚪ Eliminate (Not Urgent, Not Important)

Then provide a recommended daily schedule."""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.4,
            max_tokens=600,
        )

        return {
            "agent": "planner",
            "tasks": tasks,
            "prioritization": result["content"],
            "provider": result["provider"],
        }

    async def daily_schedule(self, goals_today: str, available_hours: int = 8) -> Dict:
        """
        আজকের জন্য daily schedule তৈরি করে।
        """
        prompt = f"""Create an optimized daily schedule:

**Today's Goals:** {goals_today}
**Available Hours:** {available_hours} hours

Create a time-blocked schedule:
- Include focus blocks (90-min deep work)
- Include breaks (Pomodoro technique)
- Include review/planning time
- Be realistic about task durations

Format: HH:MM - HH:MM | Task | Priority"""

        result = await llm_router.generate(
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=500,
        )

        return {
            "agent": "planner",
            "schedule": result["content"],
            "provider": result["provider"],
            "available_hours": available_hours,
        }


# Singleton instance
planner_agent = PlannerAgent()
