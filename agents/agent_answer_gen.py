from .base import create_agent
from state import ConversationState
from pydantic_ai import RunContext


gen_answer_agent = create_agent(
    model="openai:gpt-4o",
    deps_type=ConversationState,
)


@gen_answer_agent.system_prompt
async def answer_with_context(ctx: RunContext[ConversationState]) -> str:
    research_topic = ctx.deps.topic
    search_results = ctx.deps.search_results

    # Get the current persona's state and question
    current_persona_state = next(
        iter(ctx.deps.persona_states.values())
    )  # Get the active persona's state
    current_question = (
        current_persona_state.current_question.question
        if current_persona_state.current_question
        else None
    )

    return f"""You are a scholarly research assistant answering questions . Your responses should follow academic writing standards with proper citations and structure.

    RESEACH TOPIC:
    {research_topic}

    CURRENT QUESTION TO ANSWER:
    {current_question}

    AVAILABLE SEARCH RESULTS:
    {search_results}

    INSTRUCTIONS:
    1. Structure your response in academic paragraphs
    2. Use ONLY the provided search results
    3. Citations must be:
    - Inline citations in IEEE format as hyperlinks [[1]](link)
    - Placed immediately after the relevant claim or fact
    - Multiple citations should be comma-separated [[1]](link1), [[2]](link2)
    4. Format your response in markdown as follows:

    Response Format:
    ---------------
    Based on the research, [start your main discussion...]

    [First paragraph discussing main points with hyperlinked citations. Example: Recent studies have shown that AI algorithms can significantly improve diagnostic accuracy in medical imaging [[1]](https://doi.org/...). This improvement is particularly notable in radiology, where deep learning models have achieved performance comparable to human experts [[2]](https://doi.org/...).]

    [Second paragraph expanding on implications or additional aspects with proper citations.]

    [Concluding paragraph synthesizing the key points and implications]

    References:
    1. "[Title](link)," Year
    2. "[Title](link)," Year

    Note: Ensure each paragraph:
    - Begins with a clear topic sentence
    - Contains supporting evidence with hyperlinked citations
    - Maintains logical flow
    - Links to the next paragraph
"""


async def gen_answer(
    conv_state: ConversationState, message_history: list[str], persona_question: str
):
    editor_answer = await gen_answer_agent.run(
        f"Please provide an answer to this question: {persona_question.question}",
        deps=conv_state,
        message_history=message_history,
    )
    return editor_answer
