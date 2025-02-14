import ssl
import httpx
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

    async def asearch(self, query: str, verbose: bool = False, callback=None) -> dict:
        results = {}
        try:
            if verbose:
                print(f"Searching for: {query}")
            if callback:
                callback(f"Searching for: {query}")

            response = await self.tavily_client.search(query, max_results=self.max_results)
            search_results = response["results"]
            for r in search_results:
                if verbose:
                    print(f"Reading from: {r['url']}\n Title: {r['title']}\n")
                if callback:
                    callback(f"Reading: {r['title']}")
                    callback({"url": r["url"], "title": r["title"]})
                source = {r["url"]: r["content"]}
                results.update(source)
        except (httpx.ConnectError, ConnectionError) as e:
            error_msg = "⚠️ Connection Error: Unable to connect to search service. Please check your internet connection."
            if callback:
                callback(error_msg)
            if verbose:
                print(f"Connection error: {str(e)}")
        except ssl.SSLError as e:
            error_msg = "⚠️ SSL Error: Unable to establish secure connection. Please check your network settings."
            if callback:
                callback(error_msg)
            if verbose:
                print(f"SSL error: {str(e)}")
        except Exception as e:
            error_msg = f"⚠️ Search error: {str(e)}"
            if callback:
                callback(error_msg)
            if verbose:
                print(f"Search error: {str(e)}")
        return results

    async def abatch_search(
        self, queries: list[str], verbose: bool = False, callback=None
    ) -> dict:
        search_results = {}
        for query in queries:
            try:
                results = await self.asearch(query, verbose=verbose, callback=callback)
                search_results.update(results)
            except Exception as e:
                if verbose:
                    print(f"Batch search error: {str(e)}")
                if callback:
                    callback(f"⚠️ Error during batch search: {str(e)}")
        return search_results

    @staticmethod
    def results_to_str(search_results: dict, max_len: int = 50_000) -> str:
        return "\n\n##########\n".join(
            f"URL:\n {url}\n\nContent:\n{content}"
            for url, content in search_results.items()
        )[:max_len]
