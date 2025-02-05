from pydantic_output import RelatedTopics
from prompts import TOPIC_EXPLORER_PROMPT
from .base import create_agent
from config import FAST_MODEL

topic_explorer_agent = create_agent(
    model=FAST_MODEL,
    result_type=RelatedTopics,
    system_prompt=TOPIC_EXPLORER_PROMPT,
)


async def gen_related_topics(topic: str):
    """Run topic explorer agent"""
    related_topics = await topic_explorer_agent.run(topic)
    print(f"Looking up related topics... {', '.join(related_topics.data.topics)}\n\n")
    return related_topics.data.topics
