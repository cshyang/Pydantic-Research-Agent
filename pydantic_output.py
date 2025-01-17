from pydantic import BaseModel, Field
from typing import List


class RelatedTopics(BaseModel):
    """Return a list of related topics"""

    topics: List[str] = Field(description="A list of related topics with maximum of 3.")


class Subsection(BaseModel):
    """Subsection of the outline"""

    title: str = Field(description="The title of the subsection.")
    content: str = Field(description="The content of the subsection.")


class Section(BaseModel):
    """Section of the outline"""

    title: str = Field(description="The title of the section.")
    content: str = Field(description="The content of the section.")
    subtitles: List[Subsection] = Field(description="A list of subsections.")

    @property
    def as_str(self):
        subsections = "\n\n".join(
            f"### {s.title}\n\n {s.content}" for s in self.subtitles
        )
        return f"## {self.title}\n\n{self.content}\n\n{subsections}"


class Outline(BaseModel):
    """Final outline of the article"""

    title: str = Field(description="The title of the article.")
    sections: List[Section]

    @property
    def as_str(self):
        sections = "\n\n".join(f"{s.as_str}" for s in self.sections)
        return f"# {self.title}\n\n{sections}"
