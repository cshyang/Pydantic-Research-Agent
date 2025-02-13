from pydantic_ai import RunContext
from pydantic_output import Section
from state import ResearchContext
from prompts import SECTION_DRAFTER_PROMPT
from .base import create_agent
from config import MAX_CHAR_LIMIT

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


async def gen_section_drafts(research_context: ResearchContext):
    """Generate drafts for all sections in the outline."""
    if not research_context.has_outline:
        raise ValueError("No outline available")

    outline = research_context.current_outline

    for section in outline.sections:
        # Generate draft for main section
        draft = await section_draft_agent.run(
            f"""Write content for '{section.title}' and its subsections:\n
            {", ".join(sub.title for sub in section.subtitles)}
""",
            deps=research_context,
        )
        research_context.update_draft(draft.data)

    return research_context.current_drafts
