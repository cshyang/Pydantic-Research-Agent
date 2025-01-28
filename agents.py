from pydantic_ai import Agent, Tool, RunContext
from pydantic_output import RelatedTopics, Outline, Section, Article
from dotenv import load_dotenv
import json
from state import ResearchContext
from tools import wiki_research
from prompts import (
    TOPIC_EXPLORER_PROMPT,
    OUTLINE_GENERATOR_PROMPT,
    SECTION_DRAFTER_PROMPT,
    ARTICLE_GENERATOR_PROMPT,
)

load_dotenv()

""" Topic explorer agent """
topic_explorer_agent = Agent(
    "openai:gpt-4o-mini",
    result_type=RelatedTopics,
    system_prompt=TOPIC_EXPLORER_PROMPT,
)


async def gen_related_topics(topic: str):
    """Run topic explorer agent"""
    related_topics = await topic_explorer_agent.run(topic)
    print(f"Looking up related topics... {', '.join(related_topics.data.topics)}\n\n")
    return related_topics.data.topics


""" Generate outline agent """

gen_outline_agent = Agent(
    "openai:gpt-4o",
    result_type=Outline,
    deps_type=ResearchContext,
    system_prompt=OUTLINE_GENERATOR_PROMPT,
)


@gen_outline_agent.tool
async def get_outline_context(ctx: RunContext[ResearchContext]) -> str:
    """Research topics and return relevant information.

    Returns example outlines if no existing outline, otherwise returns current context.
    """
    if not ctx.deps.current_outline:
        return await wiki_research(ctx.deps.related_topics)
    return f"Current Outline:\n{ctx.deps.current_outline}\n\n Search Result:\n{json.dumps(ctx.deps.search_results)}"


async def gen_outline(research_context: ResearchContext):
    current_outline = await gen_outline_agent.run(
        f"Generate or update the outline for the research topic: {research_context.main_topic} based on context.",
        deps=research_context,
    )
    research_context.update_outline(current_outline.data)
    return current_outline


""" Section draft agent """

section_draft_agent = Agent(
    "openai:gpt-4o",
    result_type=Section,
    deps_type=ResearchContext,
    system_prompt=SECTION_DRAFTER_PROMPT,
)


@section_draft_agent.tool
async def get_section_context(ctx: RunContext[ResearchContext]) -> str:
    """Get relevant research for the section."""
    search_results = []
    for url, content in ctx.deps.search_results.items():
        search_results.append(f"Source: {url}\n{content}\n")
    return "\n".join(search_results)


async def gen_section_drafts(research_context: ResearchContext):
    """Generate drafts for all sections in the outline."""
    if not research_context.has_outline:
        raise ValueError("No outline available")

    outline = research_context.current_outline

    for section in outline.sections:
        # Generate draft for main section
        draft = await section_draft_agent.run(
            f"""Write content for the section and it subsections: 
            Main section:
            {section.title}
            Subjection:
            {"\n".join(f" - {sub.title}" for sub in section.subtitles)}
            Generate comprehensive content for the main section and all subsections listed above. 
            Maintain clear transitions between subsections and ensure content flows naturally.
            """,
            deps=research_context,
        )
        research_context.update_draft(draft.data)

    return research_context.current_drafts


""" Generate Article agent """
gen_article_agent = Agent(
    model="openai:gpt-4o",
    result_type=Article,
    system_prompt=ARTICLE_GENERATOR_PROMPT,
    tools=[Tool(get_section_context)],
)
