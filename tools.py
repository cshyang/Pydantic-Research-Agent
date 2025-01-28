from search_tools import TavilySearch
from langchain_community.retrievers import WikipediaRetriever
from typing import List
from state import ResearchContext


async def tavily_search(research_context: ResearchContext):
    tavily_search = TavilySearch()
    search_results = await tavily_search.abatch_search(research_context.related_topics)
    research_context.add_search_result(search_results)
    search_results_str = TavilySearch.results_to_str(search_results)
    return search_results_str


async def wiki_research(topics: List[str], top_k_results: int = 1) -> str:
    """Search on wikipedia given a topic."""
    wiki_retriever = WikipediaRetriever(top_k_results=top_k_results)
    results = await wiki_retriever.abatch(topics)
    return "\n\n".join(
        f"Title: {doc[0].metadata['title']}\n\nContent:\n {doc[0].page_content}\n\n"
        for doc in results
    )
