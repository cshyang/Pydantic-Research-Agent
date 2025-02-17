from src.tools.tavily import TavilySearch
from langchain_community.retrievers import WikipediaRetriever
from src.core.config import MAX_SEARCH_RESULT
from typing import List


async def tavily_search(queries: List[str], verbose: bool = False, callback=None):
    tavily_search = TavilySearch(max_results=MAX_SEARCH_RESULT)
    search_results = await tavily_search.abatch_search(
        queries, verbose=verbose, callback=callback
    )
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
