from pydantic_output import InterviewQuestion
from prompts import QUESTION_GENERATOR_PROMPT
from .base import create_agent
from state import ConversationState
from pydantic_ai import RunContext


gen_questions_agent = create_agent(
    model="openai:gpt-4o",
    result_type=InterviewQuestion,
    deps_type=ConversationState,
)


@gen_questions_agent.system_prompt
async def get_questions_prompt(ctx: RunContext[ConversationState]) -> str:
    persona_state = next(iter(ctx.deps.persona_states.values()))
    previous_questions = (
        "\n".join(persona_state.get_question_strings())
        if persona_state.previous_questions
        else "No previous questions"
    )

    return QUESTION_GENERATOR_PROMPT.format(
        persona=persona_state.persona.persona, previous_questions=previous_questions
    )


async def gen_questions(
    conv_state: ConversationState,
    message_history: list[str],
) -> InterviewQuestion:
    persona_question = await gen_questions_agent.run(
        f"I am working on this topic, from your perspective, what should I research?\nTopic: {conv_state.topic}",
        deps=conv_state,
        message_history=message_history,
    )
    return persona_question
