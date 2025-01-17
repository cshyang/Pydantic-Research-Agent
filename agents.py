from pydantic_ai import Agent, Tool
from pydantic_output import RelatedTopics, Outline
from tools import tavily_asearch
from dotenv import load_dotenv

load_dotenv()

topic_explorer_agent = Agent(
    "openai:gpt-4o-mini",
    result_type=RelatedTopics,
    system_prompt=(
        "You are an experienced researcher. Given a research topic, return a list of relevant topics to research on."
        "Avoid returning topics that are too broad or too specific. "
        "The list of topics will then use to research on serch engine and wikipedia to find relevant information. "
    ),
)


async def gen_related_topics(topic: str):
    """Run topic explorer agent"""
    related_topics = await topic_explorer_agent.run(topic)
    print(f"Looking up related topics... {', '.join(related_topics.data.topics)}\n\n")
    return related_topics.data.topics


gen_article_agent = Agent(
    "openai:gpt-4o",
    result_type=Outline,
    deps_type=Outline,
    system_prompt=(
        "You are an experienced researcher, given a research topic, use gen_related_topics to find more relevant topics."
        "Use tavily_search.abatch_search tool to gather relevant information with the relevant topics."
        "Based on the resouces gathered, generate a wiki article based on the outline."
        "IMPORTANT: Use only the information gathered and cite the url of the source used to contruct this wiki article."
        "Make sure the article is informative and cohesive."
    ),
    tools=[Tool(tavily_asearch), Tool(gen_related_topics)],
)

gen_outline_agent = Agent(
    "openai:gpt-4o-mini",
    result_type=Outline,
    system_prompt=(
        "You are a wiki article editor. Based on the similar wiki articles gathered, generate an outline for the wiki article."
    ),
)
