from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class RelatedTopics(BaseModel):
    """Return a list of related topics"""

    topics: List[str] = Field(description="A list of related topics with maximum of 3.")


class Citation(BaseModel):
    url: str
    title: str


class Subsection(BaseModel):
    title: str = Field(description="The title of the subsection.")
    content: str = Field(description="The content of the subsection.")
    citations: Optional[List[Citation]] = None

    @property
    def as_str(self) -> str:
        content = f"### {self.title}\n\n{self.content}"
        if self.citations:
            citations = "\nSources:\n" + "\n".join(
                f"- [{c.title}]({c.url})" for c in self.citations
            )
            content += citations
        return content


class Section(BaseModel):
    title: str = Field(description="The title of the section.")
    content: str = Field(description="The content of the section.")
    subtitles: List[Subsection] = Field(description="A list of subsections.")
    citations: Optional[List[Citation]] = None

    @property
    def as_str(self) -> str:
        content = f"## {self.title}\n\n{self.content}"
        if self.citations:
            citations = "\nSources:\n" + "\n".join(
                f"- [{c.title}]({c.url})" for c in self.citations
            )
            content += citations
        if self.subtitles:
            content += "\n\n" + "\n\n".join(s.as_str for s in self.subtitles)
        return content


class Outline(BaseModel):
    title: str = Field(description="The title of the document.")
    sections: List[Section]

    @property
    def as_str(self) -> str:
        sections = "\n\n".join(s.as_str for s in self.sections)
        return f"# {self.title}\n\n{sections}"


class OutlineDraft(BaseModel):
    """Collection of all section drafts."""

    title: str = Field(description="Article title")
    section_drafts: Dict[str, Section] = Field(
        default_factory=dict, description="Map of section titles to their drafts"
    )

    def add_draft(self, draft: Section):
        """Add or update a section draft."""
        self.section_drafts[draft.title] = draft

    @property
    def as_str(self) -> str:
        """Format all drafts as a string."""
        sections = [f"# {self.title}\n"]
        for draft in self.section_drafts.values():
            sections.append(f"## {draft.title}\n\n{draft.content}\n")
            if draft.citations:
                citations = "\nSources:\n" + "\n".join(
                    f"- [{c.title}]({c.url})" for c in draft.citations
                )
                sections.append(citations)
            if draft.subtitles:
                for sub in draft.subtitles:
                    sections.append(f"### {sub.title}\n\n{sub.content}\n")
                    if sub.citations:
                        citations = "\nSources:\n" + "\n".join(
                            f"- [{c.title}]({c.url})" for c in sub.citations
                        )
                        sections.append(citations)
        return "\n\n".join(sections)


class Article(Outline):
    """An article document with introduction."""

    introduction: str = Field(description="The introduction of the article.")

    @property
    def as_str(self) -> str:
        return f"# {self.title}\n\n{self.introduction}\n\n" + "\n\n".join(
            s.as_str for s in self.sections
        )
