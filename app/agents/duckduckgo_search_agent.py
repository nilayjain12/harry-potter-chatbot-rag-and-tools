from langchain_community.tools import DuckDuckGoSearchResults

def retrieve_search_results(query):
    """
    This function retrieves search results from DuckDuckGo using the DuckDuckGoSearchRun tool.
    If DuckDuckGo search fails, it returns an empty list and logs the error.
    
    :param query: The search query string.
    :return: A list of search results or an empty list if the search fails.
    """
    try:
        duckduckgo_search = DuckDuckGoSearchResults()
        results = duckduckgo_search.run(query)
        return results
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return []
