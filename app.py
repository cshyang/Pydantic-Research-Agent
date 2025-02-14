import streamlit as st
import asyncio
from research_agent import (
    ResearchContext,
    gen_related_topics,
    gen_outline,
    run_multi_persona_conversation,
    gen_section_drafts,
)
from config import CONVERSATION_LOOP

# Initialize Streamlit app
st.set_page_config(page_title="𖡎 BrainSTORM AI Writer", page_icon="📚", layout="wide")

# Add CSS styles for animations and chat
st.markdown(
    """
<style>
@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}
.reading-indicator {
    display: inline-block;
    animation: blink 1.5s ease-in-out infinite;
    color: #1E88E5;
    font-weight: 500;
    margin: 10px 0;
    padding: 8px 12px;
    background: rgba(30, 136, 229, 0.1);
    border-radius: 4px;
}
.reading-indicator a {
    color: #1E88E5;
    text-decoration: none;
    font-weight: 500;
}
.reading-indicator a:hover {
    text-decoration: underline;
}
/* Chat styles */
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 80%;
}
.persona {
    background-color: #e3f2fd;
    margin-right: 20%;
    border-top-left-radius: 5px;
}
.editor {
    background-color: #f3e5f5;
    margin-left: 20%;
    border-top-right-radius: 5px;
}
.chat-container {
    margin: 10px 0;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("AI Research Assistant")
st.markdown("""
This tool helps you research any topic using multiple AI personas to gather diverse perspectives.
Each persona will ask questions and provide insights based on their unique viewpoint.
""")

# Initialize session state
if "research_context" not in st.session_state:
    st.session_state.research_context = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "outline_generated" not in st.session_state:
    st.session_state.outline_generated = False
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False
if "drafts_complete" not in st.session_state:
    st.session_state.drafts_complete = False
if "conversation_messages" not in st.session_state:
    st.session_state.conversation_messages = []
if "full_conversation_history" not in st.session_state:
    st.session_state.full_conversation_history = []
if "current_persona" not in st.session_state:
    st.session_state.current_persona = None
if "persona_count" not in st.session_state:
    st.session_state.persona_count = 0
if "current_sources" not in st.session_state:
    st.session_state.current_sources = []
if "completed_sections" not in st.session_state:
    st.session_state.completed_sections = []

# Input section
if st.session_state.current_step == 0:
    st.header("Step 1: Enter Research Topic")
    research_topic = st.text_input("What topic would you like to research?")

    if st.button("Start Research"):
        if research_topic:
            st.session_state.research_context = ResearchContext(
                main_topic=research_topic
            )
            st.session_state.current_step = 1
            st.rerun()
        else:
            st.error("Please enter a research topic")

# Generate related topics
elif st.session_state.current_step == 1:
    st.header("Step 2: Generating Related Topics")
    with st.spinner("Generating related topics..."):
        asyncio.run(gen_related_topics(st.session_state.research_context.main_topic))
        st.session_state.current_step = 2
        st.rerun()

# Generate initial outline
elif st.session_state.current_step == 2:
    st.header("Step 3: Generating Initial Outline")
    with st.spinner("Generating initial outline..."):
        asyncio.run(gen_outline(st.session_state.research_context))
        st.session_state.outline_generated = True
        st.session_state.current_step = 3
        st.rerun()

# Run multi-persona conversation
elif st.session_state.current_step == 3:
    st.header("Step 4: Multi-Persona Research")

    # Create placeholders for status and current question
    status_placeholder = st.empty()
    current_question = st.empty()
    progress_bar = st.empty()

    if not st.session_state.conversation_complete:
        with st.spinner("Brainforming with different perspectives..."):
            # Function to update progress
            def update_progress(message):
                # Store all messages in full history
                st.session_state.full_conversation_history.append(message)

                # Handle string messages
                if isinstance(message, str):
                    # Update persona progress
                    if message.startswith("Research topic"):
                        st.session_state.current_persona = message.split(": ")[1]
                        st.session_state.persona_count += 1
                        status_placeholder.markdown(
                            f"🤖 **Current Persona ({st.session_state.persona_count}/3):** _{st.session_state.current_persona}_"
                        )
                        progress_bar.progress(st.session_state.persona_count / 3)

                    # Show current question in a styled container
                    elif message.startswith("Question from"):
                        # Clear previous sources when a new question starts
                        st.session_state.current_sources = []
                        st.session_state.full_conversation_history.append(message)
                        with current_question.container():
                            st.markdown("---")
                            st.markdown(f"🤔 _{message}_")
                            st.markdown("---")

                    # Initialize sources list when starting a new search
                    elif message.startswith("🔍 Searching for:"):
                        if "current_sources" not in st.session_state:
                            st.session_state.current_sources = []
                        st.session_state.current_sources = []
                        # Show searching message with animation
                        with current_question.container():
                            st.markdown("---")
                            st.markdown(
                                f'<div class="reading-indicator">🔍 {message}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown("---")

                    # Handle error messages
                    elif message.startswith("⚠️"):
                        with current_question.container():
                            st.markdown("---")
                            st.error(message)
                            st.markdown("---")

                # Handle dictionary messages (search results)
                elif (
                    isinstance(message, dict)
                    and "title" in message
                    and "url" in message
                ):
                    st.session_state.current_sources.append(message)
                    # Update the current question container to show sources
                    with current_question.container():
                        st.markdown("---")
                        # Get the last question from history
                        last_question = next(
                            (
                                msg
                                for msg in reversed(
                                    st.session_state.full_conversation_history
                                )
                                if isinstance(msg, str)
                                and msg.startswith("Question from")
                            ),
                            None,
                        )
                        if last_question:
                            st.markdown(f"🤔 _{last_question}_")
                        st.markdown(
                            "📚 Reading from sources...",
                            unsafe_allow_html=True,
                        )
                        for source in st.session_state.current_sources[
                            :3
                        ]:  # Show top 3 sources
                            st.markdown(
                                f'<div class="reading-indicator">- <a href="{source["url"]}" target="_blank">{source["title"]}</a></div>',
                                unsafe_allow_html=True,
                            )
                        st.markdown("---")

            asyncio.run(
                run_multi_persona_conversation(
                    research_context=st.session_state.research_context,
                    num_rounds=CONVERSATION_LOOP,
                    verbose=True,
                    progress_callback=update_progress,
                )
            )
            st.session_state.conversation_complete = True
            st.rerun()
    else:
        # Clear temporary displays
        status_placeholder.empty()
        current_question.empty()
        progress_bar.empty()

        # Show a summary of the conversation
        st.success("Persona conversations complete!")

        # Show questions grouped by persona
        questions_by_persona = {}
        for msg in st.session_state.full_conversation_history:
            if isinstance(msg, str) and msg.startswith("Question from"):
                persona = msg.split("Question from ")[1].split(":")[0]
                question = msg.split(": ", 1)[1]
                if persona not in questions_by_persona:
                    questions_by_persona[persona] = []
                questions_by_persona[persona].append(question)

        # Display questions grouped by persona in an expander
        with st.expander("📝 View All Questions"):
            for persona, questions in questions_by_persona.items():
                st.markdown(f"**Questions from {persona}:**")
                for q in questions:
                    st.markdown(f"- _{q}_")
                st.markdown("---")

        st.session_state.current_step = 4
        st.rerun()

# Generate section drafts
elif st.session_state.current_step == 4:
    st.header("Step 5: Generating Article")

    if not st.session_state.drafts_complete:
        # Create placeholders for status
        status_placeholder = st.empty()
        progress_placeholder = st.empty()

        with st.spinner("Drafting section..."):
            # Reset completed sections
            st.session_state.completed_sections = []

            # Function to track drafting progress
            def drafting_progress(message):
                if isinstance(message, str):
                    if message.startswith("Drafting section:"):
                        # Extract section title and show with animation
                        section = message.split("Drafting section:", 1)[1].strip()
                        status_placeholder.markdown(
                            f'<div class="reading-indicator">✍️ Drafting section: _{section}_...</div>',
                            unsafe_allow_html=True,
                        )
                    elif message.startswith("Section complete:"):
                        # Show completed section
                        section = message.split("Section complete:", 1)[1].strip()
                        # Add to completed sections
                        st.session_state.completed_sections.append(section)
                        # Display all completed sections with each on a new line
                        completed_sections_text = ""
                        for section in st.session_state.completed_sections:
                            completed_sections_text += (
                                f"✅ Completed section: _{section}_\n\n"
                            )
                        progress_placeholder.markdown(completed_sections_text)

            asyncio.run(
                gen_section_drafts(
                    st.session_state.research_context,
                    progress_callback=drafting_progress,
                )
            )
            st.session_state.drafts_complete = True
            st.rerun()
    else:
        # Display final results
        st.success("Research Complete! 🎉")

        # Add download button for the article
        if st.session_state.research_context.current_drafts:
            article_md = st.session_state.research_context.current_drafts.as_str
            st.download_button(
                "📥 Download Article as Markdown",
                article_md,
                file_name=f"{st.session_state.research_context.main_topic.replace(' ', '_')}.md",
                mime="text/markdown",
            )

            # Display the article in tabs - one for reading view, one for conversations
            tab1, tab2 = st.tabs(["📖 Reading View", "💬 Conversations"])

            with tab1:
                st.markdown(article_md)

            with tab2:
                # Get all personas from the complete conversation history
                personas = list(
                    st.session_state.research_context.complete_conversation_history.keys()
                )
                persona_tabs = st.tabs([f"👤 {persona}" for persona in personas])

                # Function to display a chat message
                def display_chat_message(
                    role: str, message: str, is_editor: bool = False
                ):
                    align = "right" if is_editor else "left"
                    bubble_class = "editor" if is_editor else "persona"
                    st.markdown(
                        f"""
                    <div class="chat-container" style="text-align: {align}">
                        <div class="chat-bubble {bubble_class}">
                            <small><strong>{role}</strong></small><br>
                            {message}
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Display conversations for each persona
                for tab, persona in zip(persona_tabs, personas):
                    with tab:
                        st.markdown(f"### Conversation with {persona}")

                        # Get conversation history for this persona
                        conversation = st.session_state.research_context.complete_conversation_history.get(
                            persona, []
                        )

                        if conversation:
                            for entry in conversation:
                                if entry["role"] == persona:
                                    display_chat_message(persona, entry["content"])
                                elif entry["role"] == "editor":
                                    display_chat_message(
                                        "Editor", entry["content"], True
                                    )
                        else:
                            st.info("No conversation found for this persona.")

        # Reset button
        if st.button("Start New Research"):
            st.session_state.clear()
            st.rerun()

# Progress bar
if st.session_state.current_step > 0:
    progress = st.session_state.current_step / 4
    st.progress(progress)
