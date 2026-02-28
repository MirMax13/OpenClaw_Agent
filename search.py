from ddgs import DDGS

class InternetSearchTool:
    def __init__(self, max_results=3):
        self.max_results = max_results

    def search(self, query):
        print(f"Performing internet search for: {query}")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                return "No results found."
            
            formatted_results = "Search results:\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\nSnippet: {result['body']}\n\n"
            
            return formatted_results
        except Exception as e:
            print(f"Error during search: {e}")
            return "Sorry, I couldn't perform the search at this time."
    
