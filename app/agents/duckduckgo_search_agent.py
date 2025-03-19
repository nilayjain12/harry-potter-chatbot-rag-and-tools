# importing required libraries
from langchain_community.tools import DuckDuckGoSearchResults

def retrieve_search_results(query):
    """
    This function retrieves search results from DuckDuckGo using the DuckDuckGoSearchRun tool.
    
    :param query: The search query string.
    :return: A list of search results.
    """
    # Initialize the DuckDuckGo search tool
    duckduckgo_search = DuckDuckGoSearchResults()
    
    # Perform the search and get results
    results = duckduckgo_search.run(query)
    
    return results