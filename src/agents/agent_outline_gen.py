from pydantic_ai import RunContext
from src.core.pydantic_models import Outline
from src.core.state import ResearchContext
from src.tools.search_tools import wiki_research
from src.core.prompts import OUTLINE_GENERATOR_PROMPT
from .base import create_agent
from src.core.config import DEFAULT_MODEL

gen_outline_agent = create_agent(
    DEFAULT_MODEL,
    result_type=Outline,
    deps_type=ResearchContext,
    system_prompt=OUTLINE_GENERATOR_PROMPT,
)


@gen_outline_agent.tool
async def get_outline_context(ctx: RunContext[ResearchContext]) -> str:
    """Research topics and return relevant information.

    If no outline exists:
        Returns example outlines from wiki research
    If outline exists:
        Returns current outline and conversation history for context
    """
    if not ctx.deps.current_outline:
        return await wiki_research(ctx.deps.related_topics)

    # Format conversation history into a readable context
    conversation_context = ""
    if ctx.deps.current_persona_history:  # Use current_persona_history instead
        conversation_context = "Recent Conversations:\n"
        for entry in ctx.deps.current_persona_history:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            conversation_context += f"{role}: {content}\n"

    return f"""Current Outline:
{ctx.deps.current_outline}

Recent Conversations and Insights:
{conversation_context}
"""


async def gen_outline(research_context: ResearchContext):
    """Generate or update research outline."""
    current_outline = await gen_outline_agent.run(
        f"Generate or update the outline for the research topic: {research_context.main_topic} based on context.",
        deps=research_context,
    )
    research_context.update_outline(current_outline.data)
    return current_outline
