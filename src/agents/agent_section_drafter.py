from pydantic_ai import RunContext
from src.core.pydantic_models import Section, OutlineDraft
from src.core.state import ResearchContext
from src.core.config import MAX_CHAR_LIMIT
from src.core.prompts import SECTION_DRAFTER_PROMPT
from .base import create_agent
from .agent_outline_gen import gen_outline

section_draft_agent = create_agent(
    "openai:gpt-4o",
    result_type=Section,
    deps_type=ResearchContext,
    system_prompt=SECTION_DRAFTER_PROMPT,
)


@section_draft_agent.tool
async def get_section_context(ctx: RunContext[ResearchContext]) -> str:
    """
    Returns both search results and conversations from different perspectives
    to provide a comprehensive context for section writing.
    """
    # Get conversations from different perspectives
    conversation_context = []
    for perspective, entries in ctx.deps.complete_conversation_history.items():
        conversation_context.append(f"\nPerspective: {perspective}")
        for entry in entries:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            # Skip the conversation markers in the content
            content = content.replace("---------------\n", "")
            # Limit the length of each conversation entry
            if len(content) > MAX_CHAR_LIMIT:
                content = content[: MAX_CHAR_LIMIT - 3] + "..."
            conversation_context.append(f"{role}: {content}\n")

    return f"""
Expert Perspectives and Discussions:
{"-" * 80}
{"".join(conversation_context)}
"""


async def gen_section_drafts(research_context: ResearchContext, progress_callback=None):
    """Generate drafts for each section in the outline."""
    if not research_context.current_outline:
        await gen_outline(research_context)

    if progress_callback:
        progress_callback("Starting to draft sections...")

    # Create an OutlineDraft object
    outline_draft = OutlineDraft(title=research_context.current_outline.title)

    # Generate drafts for each section
    for section in research_context.current_outline.sections:
        if progress_callback:
            progress_callback(f"Drafting section: {section.title}")

        # Generate draft for this section
        draft = await section_draft_agent.run(
            f"""Write content for '{section.title}' and its subsections:\n
            {", ".join(sub.title for sub in section.subtitles)}
""",
            deps=research_context,
        )

        # Add the draft to our OutlineDraft object
        outline_draft.add_draft(draft.data)

        if progress_callback:
            progress_callback(f"Section complete: {section.title}")

    # Update research context with the outline draft
    research_context.current_drafts = outline_draft

    return research_context.current_drafts
