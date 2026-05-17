from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.base_agent import BaseAgent
from google.adk.events import Event, EventActions
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

load_dotenv()

MODEL = "gemini-2.0-flash"

# Conexión al Researcher (puerto 8001)
from google.adk.agents import RemoteA2aAgent

def create_save_output_callback(key: str):
    async def callback(ctx: InvocationContext, output: str):
        ctx.session.state[key] = output
    return callback

researcher = RemoteA2aAgent(
    name="researcher",
    agent_card="http://localhost:8001/a2a/agent/.well-known/agent-card.json",
    description="Gathers information using Google Search.",
    after_agent_callback=create_save_output_callback("research_findings"),
)

# Conexión al Judge (puerto 8002)
judge = RemoteA2aAgent(
    name="judge",
    agent_card="http://localhost:8002/a2a/agent/.well-known/agent-card.json",
    description="Evaluates research.",
    after_agent_callback=create_save_output_callback("judge_feedback"),
)

# Conexión al Content Builder (puerto 8003)
content_builder = RemoteA2aAgent(
    name="content_builder",
    agent_card="http://localhost:8003/a2a/agent/.well-known/agent-card.json",
    description="Builds the course.",
)

# EscalationChecker — lógica pura en Python, sin LLM
class EscalationChecker(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        feedback = ctx.session.state.get("judge_feedback")
        print(f"[EscalationChecker] Feedback: {feedback}")

        is_pass = False
        if isinstance(feedback, dict) and feedback.get("status") == "pass":
            is_pass = True
        elif isinstance(feedback, str) and '"status": "pass"' in feedback:
            is_pass = True

        if is_pass:
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)

escalation_checker = EscalationChecker(name="escalation_checker")

# LoopAgent — bucle de investigación
research_loop = LoopAgent(
    name="research_loop",
    description="Iteratively researches and judges until quality standards are met.",
    sub_agents=[researcher, judge, escalation_checker],
    max_iterations=3,
)

# SequentialAgent — pipeline completo
root_agent = SequentialAgent(
    name="course_creation_pipeline",
    description="A pipeline that researches a topic and then builds a course from it.",
    sub_agents=[research_loop, content_builder],
)