from agents import (
    gen_related_topics,
    gen_outline,
    gen_section_drafts,
    gen_article,
    gen_personas,
    gen_questions,
    gen_answer,
)
from tools import tavily_search
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
from state import ResearchContext, ConversationState
from helper import to_chat_message
from config import CONVERSATION_LOOP
import asyncio


async def run_multi_persona_conversation(
    research_context: ResearchContext,
    num_rounds: int = CONVERSATION_LOOP,
    verbose: bool = False,
):
    # Initialize conversation state for managing personas
    conv_state = ConversationState(topic=research_context.main_topic)
    personas = await gen_personas(research_context)
    for persona in personas:
        conv_state.add_persona(persona)

    conversation_history = []
    message_history = []

    # Iterate through each persona for questions
    for persona in personas:
        print(f"Research topic based on the perspective: {persona.role}")
        for round_num in range(num_rounds):
            persona_state = conv_state.get_persona_state(persona.role)

            # Generate question for current persona
            persona_question = await gen_questions(conv_state, message_history)

            # Update persona state
            persona_state.current_question = persona_question.data
            persona_state.previous_questions.append(persona_question.data)

            # Search and get results
            queries = persona_question.data.queries
            conv_state.search_results = await tavily_search(queries)

            # Create conversation entries
            question_entry = to_chat_message(
                persona_question.new_messages(), role=persona.role
            )
            conversation_history.append(question_entry)

            # Get editor answer with context
            editor_answer = await gen_answer(
                conv_state, message_history, persona_question.data
            )

            # Create answer entry and update history
            answer_entry = to_chat_message(editor_answer.new_messages(), role="editor")
            conversation_history.append(answer_entry)

            # Update message history
            message_history.extend(persona_question.new_messages())
            message_history.extend(editor_answer.new_messages())

            # Update both complete and current persona conversation histories
            research_context.update_conversation_history(
                [question_entry, answer_entry], persona.role
            )
            if verbose:
                print(f"Round {round_num + 1}, Persona: {persona.role}")
                print(f"Question: {persona_question.data.question}\n")
                print(f"Answer: {editor_answer.data}\n")
                print("-" * 80 + "\n")

        # Update the outline using only this persona's conversation
        await gen_outline(research_context)

        # Clear only the current persona's history
        research_context.clear_current_persona_history()

    return conversation_history


async def main():
    console = Console()

    # Step 1: Get research topic and initialize context
    research_topic = Prompt.ask("What topic would you like to research on?")
    research_context = ResearchContext(main_topic=research_topic)

    # Step 2: Generate related topics
    console.print("\n[bold]Generating related topics...[/bold]")
    await gen_related_topics(research_context.main_topic)

    # Step 3: Generate initial outline
    console.print("\n[bold]Generating initial outline...[/bold]")
    await gen_outline(research_context)

    # Step 4: Research based on different perspectives
    console.print("\n[bold]Generating conversation with personas...[/bold]")
    await run_multi_persona_conversation(
        research_context=research_context,
        num_rounds=2,  # or any number you prefer
    )

    # Step 5: Update outline based on conversation from different perspectives
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
