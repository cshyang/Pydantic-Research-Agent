from dotenv import load_dotenv

load_dotenv()

from agents import (
    gen_related_topics,
    gen_outline,
    gen_section_drafts,
    gen_article,
)
from tools import tavily_search
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
from state import ResearchContext
import asyncio


async def main():
    console = Console()

    # Step 1: Get research topic and initialize context
    research_topic = Prompt.ask("What topic would you like to research on?")
    research_context = ResearchContext(main_topic=research_topic)

    # Step 2: Generate related topics
    console.print("\n[bold]Generating related topics...[/bold]")
    await gen_related_topics(research_context.main_topic)

    # Step 3: Generate initial outline
    console.print("\n[bold]Generating outline...[/bold]")
    await gen_outline(research_context)

    # Step 4: Search for relevant information
    await tavily_search(research_context)

    # Step 5: Refine outline based on research
    await gen_outline(research_context)

    # Step 6: Generate section drafts
    console.print("\n[bold]Generating section drafts...[/bold]")
    await gen_section_drafts(research_context)

    # Step 7: Generate article
    console.print("\n[bold]Generating article...[/bold]")
    final_article = await gen_article(research_context)

    # Step 6: Display article
    md = Markdown(final_article.data.as_str)
    console.print(md)


if __name__ == "__main__":
    asyncio.run(main())
