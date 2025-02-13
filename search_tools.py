from tavily import AsyncTavilyClient
from dotenv import load_dotenv
from config import MAX_SEARCH_RESULT
import os

load_dotenv()


class TavilySearch:
    """Inititate Tavily Search Client"""

    def __init__(self, max_results: int = MAX_SEARCH_RESULT):
        TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "API Key Not Found")
        self.tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
        self.max_results = max_results

    async def asearch(self, query: str) -> dict:
        results = {}
        response = await self.tavily_client.search(query, max_results=self.max_results)
        print(f"Searching for: {query}")
        search_results = response["results"]
        for r in search_results:
            print(f"Reading from: {r['url']}\n Title: {r['title']}\n")
            source = {r["url"]: r["content"]}
            results.update(source)
        return results

    async def abatch_search(self, queries: list[str]) -> dict:
        search_results = {}
        for query in queries:
            results = await self.asearch(query)
            search_results.update(results)
        return search_results

    @staticmethod
    def results_to_str(search_results: dict, max_len: int = 50_000) -> str:
        return "\n\n##########\n".join(
            f"URL:\n {url}\n\nContent:\n{content}"
            for url, content in search_results.items()
        )[:max_len]
