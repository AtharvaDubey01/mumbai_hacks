import asyncio
from app.agents.verifier import search_newsapi, search_web

async def main():
    # Try quoted query for better relevance
    query = '"The earth is flat"'
    print(f"Searching for: '{query}'")
    
    print("\n--- NewsAPI Results ---")
    news_results = await search_newsapi(query)
    for r in news_results:
        print(f"Title: {r['title']}")
        print(f"Link: {r['link']}")
        print(f"Source: {r['source']}")
        print("-" * 20)
        
    print("\n--- Google CSE Results ---")
    # We need to debug why this is empty. Let's call the API manually here to see the response.
    from app.config import settings
    import aiohttp
    
    # Try the OTHER key provided by the user
    # AIzaSyAFZeVQtDX5-bEx_EaY43GhnnmUt7fRCpE
    test_key = 'AIzaSyAFZeVQtDX5-bEx_EaY43GhnnmUt7fRCpE'
    
    if settings.GOOGLE_CSE_ID:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': test_key, 'cx': settings.GOOGLE_CSE_ID, 'q': query, 'num': 5}
        print(f"Calling Google API with ALTERNATIVE KEY: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                print(f"Status: {resp.status}")
                data = await resp.json()
                if 'error' in data:
                    print(f"Error: {data['error']}")
                items = data.get('items', [])
                print(f"Found {len(items)} items")
                for i in items:
                    print(f"Title: {i.get('title')}")
                    print(f"Link: {i.get('link')}")
    else:
        print("Google Keys missing in settings!")

if __name__ == "__main__":
    asyncio.run(main())
