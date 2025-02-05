from pydantic_ai import RunContext
from pydantic_output import Section
from state import ResearchContext
from prompts import SECTION_DRAFTER_PROMPT
from .base import create_agent

section_draft_agent = create_agent(
    "openai:gpt-4o",
    result_type=Section,
    deps_type=ResearchContext,
    system_prompt=SECTION_DRAFTER_PROMPT,
)


@section_draft_agent.tool
async def get_section_context(ctx: RunContext[ResearchContext]) -> str:
    """Get relevant research for the section."""
    return "\n".join(
        f"Source: {url}\n{content}\n"
        for url, content in ctx.deps.search_results.items()
    )


async def gen_section_drafts(research_context: ResearchContext):
    """Generate drafts for all sections in the outline."""
    if not research_context.has_outline:
        raise ValueError("No outline available")

    outline = research_context.current_outline
    for section in outline.sections:
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
