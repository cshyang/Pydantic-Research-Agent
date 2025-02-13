from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pydantic_output import (
    Section,
    Outline,
    OutlineDraft,
    Article,
    Persona,
    PersonaConversation,
)


class ResearchContext(BaseModel):
    """Context for managing the state of research across agents."""

    # Core research information
    main_topic: str = Field(description="The main topic being researched")
    related_topics: List[str] = Field(
        default_factory=list, description="Related topics discovered"
    )

    # Document states
    current_outline: Optional[Outline] = Field(
        default=None, description="Current state of the outline"
    )

    current_drafts: Optional[OutlineDraft] = Field(
        default=None, description="Current state of section drafts"
    )

    current_article: Optional[Article] = Field(
        default=None, description="Current state of the article if generated"
    )

    # Conversation histories
    complete_conversation_history: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Complete history of conversations for each persona",
    )
    current_persona_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Current persona's conversation history for outline generation",
    )

    def update_conversation_history(
        self, entries: List[Dict[str, Any]], persona_role: str
    ) -> None:
        """Update both the complete and current persona conversation histories.

        Args:
            entries: List of conversation entries to add
            persona_role: Role of the current persona
        """
        # Update complete history for this persona
        if persona_role not in self.complete_conversation_history:
            self.complete_conversation_history[persona_role] = []
        self.complete_conversation_history[persona_role].extend(entries)

        # Update current persona history for outline generation
        self.current_persona_history.extend(entries)

    def clear_current_persona_history(self) -> None:
        """Clear the current persona's conversation history after outline generation."""
        self.current_persona_history = []

    def update_related_topics(self, topics: List[str]):
        """Update the related topics from topic expansion."""
        self.related_topics = topics

    def update_outline(self, outline: Outline):
        """Update the current outline."""
        self.current_outline = outline

    def update_draft(self, draft: Section):
        """Add or update a section draft."""
        if self.current_drafts is None:
            self.current_drafts = OutlineDraft(title=self.main_topic)
        self.current_drafts.add_draft(draft)

    @property
    def has_outline(self) -> bool:
        """Check if we have an existing outline."""
        return self.current_outline is not None


class ConversationState(BaseModel):
    topic: str
    search_results: Optional[str] = None
    persona_states: Dict[str, PersonaConversation] = Field(default_factory=dict)

    def add_persona(self, persona: Persona):
        """Add a new persona to track"""
        self.persona_states[persona.role] = PersonaConversation(persona=persona)

    def get_persona_state(self, role: str) -> PersonaConversation:
        """Get the state for a specific persona"""
        return self.persona_states[role]
