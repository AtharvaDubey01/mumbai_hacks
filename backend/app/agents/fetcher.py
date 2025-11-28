import aiohttp
import asyncio
from ..config import settings
from ..db import raw_items
from ..utils import now_iso
from bs4 import BeautifulSoup

# Simple NewsAPI fetcher + basic scraping for additional metadata

NEWSAPI_URL = 'https://newsapi.org/v2/top-headlines'

async def fetch_news():
    if not settings.NEWSAPI_KEY:
        print('NEWSAPI_KEY not set, skipping news fetch')
        return []
    params = {'apiKey': settings.NEWSAPI_KEY, 'language': 'en', 'pageSize': 20}
    async with aiohttp.ClientSession() as session:
        async with session.get(NEWSAPI_URL, params=params, timeout=30) as resp:
            data = await resp.json()
    articles = data.get('articles', [])
    to_store = []
    for a in articles:
        item = {
            'source': a.get('source', {}).get('name', 'newsapi'),
            'url': a.get('url'),
            'title': a.get('title'),
            'summary': a.get('description'),
            'fetched_at': now_iso(),
            'meta': {}
        }
        # optionally scrape the article for more text
        if item['url']:
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(item['url'], timeout=15) as r:
                        if r.status == 200:
                            txt = await r.text()
                            soup = BeautifulSoup(txt, 'html.parser')
                            paragraphs = [p.get_text() for p in soup.find_all('p')]
                            item['meta']['full_text'] = '\n'.join(paragraphs[:20])
            except Exception:
                pass
        res = await raw_items.insert_one(item)
        item['_id'] = str(res.inserted_id)
        to_store.append(item)
    return to_store
