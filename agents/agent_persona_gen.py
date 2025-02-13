from pydantic_output import Perspectives
from prompts import PERSONA_GENERATOR_PROMPT
from .base import create_agent
from state import ResearchContext


async def gen_personas(research_context: ResearchContext):
    gen_personas_agent = create_agent(
        "openai:gpt-4o",
        result_type=Perspectives,
        system_prompt=PERSONA_GENERATOR_PROMPT.format(
            examples=research_context.current_outline
        ),
    )
    response = await gen_personas_agent.run(", ".join(research_context.related_topics))
    return response.data.personas
