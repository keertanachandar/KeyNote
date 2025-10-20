from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class TavilySearcher:
    """Agent that searches the web for current music trends and examples"""
    
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in .env file")
        self.client = TavilyClient(api_key=api_key)
    
    def search_current_examples(self, query, max_results=3):
        """
        Search for current songs/artists using similar progressions
        
        Args:
            query (str): Search query
            max_results (int): Number of results to return
            
        Returns:
            list: Search results with title, content, url
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', 'No title'),
                    'content': result.get('content', 'No content'),
                    'url': result.get('url', '')
                })
            
            return results
        
        except Exception as e:
            print(f"⚠️  Tavily search error: {e}")
            return []