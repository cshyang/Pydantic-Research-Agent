from src.core.pydantic_models import Article
from src.core.prompts import ARTICLE_GENERATOR_PROMPT
from .base import create_agent
from src.core.state import ResearchContext


gen_article_agent = create_agent(
    model="openai:gpt-4o",
    result_type=Article,
    system_prompt=ARTICLE_GENERATOR_PROMPT,
)


async def gen_article(research_context: ResearchContext) -> str:
    """Create article generation agent with context-specific prompt."""
    result = await gen_article_agent.run(
        f"Write an wiki article using this draft:\n\n {research_context.current_drafts.as_str}",
        deps=research_context,
    )
    return result
