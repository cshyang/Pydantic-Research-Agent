from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_output import Section, Outline, OutlineDraft, Article


class ResearchContext(BaseModel):
    """Context for managing the state of research across agents."""

    # Core research information
    main_topic: str = Field(description="The main topic being researched")
    related_topics: List[str] = Field(
        default_factory=list, description="Related topics discovered"
    )

    # Research results
    search_results: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of URLs to their content from search results",
    )
    wiki_results: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of titles to content from Wikipedia research",
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

    def update_related_topics(self, topics: List[str]):
        """Update the related topics from topic expansion."""
        self.related_topics = topics

    def update_outline(self, outline: Outline):
        """Update the current outline."""
        self.current_outline = outline

    def add_search_result(self, results: Dict[str, str]):
        """Add a new search result."""
        for url, content in results.items():
            if url not in self.search_results:
                self.search_results[url] = content

    def update_draft(self, draft: Section):
        """Add or update a section draft."""
        if self.current_drafts is None:
            self.current_drafts = OutlineDraft(title=self.main_topic)
        self.current_drafts.add_draft(draft)

    def update_article(self, article: Article):
        """Update the current article."""
        self.current_article = article

    @property
    def has_outline(self) -> bool:
        """Check if we have an existing outline."""
        return self.current_outline is not None
