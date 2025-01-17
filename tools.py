from search_tools import TavilySearch


async def tavily_asearch(qieries: list):
    """Run tavily search client"""
    tavily_search = TavilySearch()
    search_results = await tavily_search.abatch_search(qieries)
    return TavilySearch.results_to_str(search_results)
