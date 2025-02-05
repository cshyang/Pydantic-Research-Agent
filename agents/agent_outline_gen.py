from pydantic_ai import RunContext
from pydantic_output import Outline
from state import ResearchContext
from tools import wiki_research
from prompts import OUTLINE_GENERATOR_PROMPT
from .base import create_agent
import json

gen_outline_agent = create_agent(
    "openai:gpt-4o",
    result_type=Outline,
    deps_type=ResearchContext,
    system_prompt=OUTLINE_GENERATOR_PROMPT,
)


@gen_outline_agent.tool
async def get_outline_context(ctx: RunContext[ResearchContext]) -> str:
    """Research topics and return relevant information."""
    if not ctx.deps.current_outline:
        return await wiki_research(ctx.deps.related_topics)
    return f"Current Outline:\n{ctx.deps.current_outline}\n\n Search Result:\n{json.dumps(ctx.deps.search_results)}"


async def gen_outline(research_context: ResearchContext):
    """Generate or update research outline."""
    current_outline = await gen_outline_agent.run(
        f"Generate or update the outline for the research topic: {research_context.main_topic} based on context.",
        deps=research_context,
    )
    research_context.update_outline(current_outline.data)
    return current_outline
