from agents import gen_article_agent
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
import asyncio


async def main():
    research_topic = Prompt.ask("What topic would you like to research on?")
    article = await gen_article_agent.run(research_topic)
    console = Console()
    md = Markdown(article.data.as_str)
    console.print(md)


if __name__ == "__main__":
    asyncio.run(main())
