# Verifier combines multiple signal sources:
# 1) Decompose claim into sub-questions (Decomposer Agent)
# 2) Search for evidence for each sub-question (Search Agent)
# 3) Use an LLM to assess the claim against evidence (Verifier Agent)

import aiohttp
import asyncio
import json
from ..db import claims, verifications
from ..config import settings
from ..utils import now_iso

# --- 1. Decomposer Agent ---
async def decompose_claim(claim_text):
    """
    Breaks a complex claim into atomic sub-questions for targeted searching.
    """
    if not settings.OPENAI_API_KEY:
        return [claim_text]

    prompt = f"""
    You are a helpful research assistant. Break down the following claim into 2-4 specific, factual search queries that would help verify it.
    
    Claim: "{claim_text}"
    
    Guidelines:
    - If the claim is simple, just return the claim itself.
    - If the claim is absurd (e.g. "Elon Musk is alien"), ask about the subject's species/biography AND the origin of the meme/conspiracy.
    - If the claim is complex, split it into component facts.
    
    Output format (JSON):
    {{
        "queries": ["query 1", "query 2", ...]
    }}
    """
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a research planner."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers) as resp:
                if resp.status != 200:
                    return [claim_text]
                result = await resp.json()
                content = result['choices'][0]['message']['content']
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(content)
                return parsed.get('queries', [claim_text])
    except Exception as e:
        print(f"Decomposer Error: {e}")
        return [claim_text]

# --- 2. Search Agent ---
async def search_web(query):
    # Use Google Custom Search JSON API if available
    if settings.GOOGLE_CSE_API_KEY and settings.GOOGLE_CSE_ID:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': settings.GOOGLE_CSE_API_KEY, 'cx': settings.GOOGLE_CSE_ID, 'q': query, 'num': 5}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            items = data.get('items', [])
            results = [{'title': i.get('title'), 'snippet': i.get('snippet'), 'link': i.get('link'), 'source': i.get('displayLink')} for i in items]
            return results
        except Exception:
            return []
    return []

async def search_newsapi(query):
    if not settings.NEWSAPI_KEY:
        return []
    url = 'https://newsapi.org/v2/everything'
    params = {
        'apiKey': settings.NEWSAPI_KEY,
        'q': query,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
        articles = data.get('articles', [])
        return [{
            'title': a.get('title'),
            'snippet': a.get('description'),
            'link': a.get('url'),
            'source': a.get('source', {}).get('name', 'NewsAPI')
        } for a in articles]
    except Exception:
        return []

async def search_reddit(query):
    url = 'https://www.reddit.com/search.json'
    params = {'q': query, 'sort': 'relevance', 'limit': 5, 'type': 'link,self'}
    headers = {'User-Agent': 'MisinfoAgent/1.0'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
        
        children = data.get('data', {}).get('children', [])
        results = []
        for child in children:
            d = child.get('data', {})
            results.append({
                'title': d.get('title'),
                'snippet': d.get('selftext') or d.get('title'),
                'link': f"https://www.reddit.com{d.get('permalink')}",
                'source': f"Reddit ({d.get('subreddit_name_prefixed')})"
            })
        return results
    except Exception:
        return []

# --- 3. Verifier Agent ---
async def score_with_llm(claim_text, evidence):
    if not settings.OPENAI_API_KEY:
        return None, 0.0, []

    # Prepare evidence text
    evidence_text = ""
    for i, e in enumerate(evidence):
        source = e.get('source', 'Unknown')
        snippet = e.get('snippet', '')
        title = e.get('title', '')
        evidence_text += f"Source {i+1} ({source}): {title} - {snippet}\n"

    prompt = f"""
    You are an expert fact-checker using a "Chain of Thought" reasoning process.
    
    Claim: "{claim_text}"
    
    Evidence:
    {evidence_text}
    
    Instructions:
    1. Analyze the evidence. Is there scientific consensus? Are there reliable sources?
    2. Check for absurdity. If the claim contradicts basic biological/physical facts (e.g. "person is alien", "earth is flat") and has no scientific backing, it is FALSE or SATIRE.
    3. Check source credibility. Disregard "evidence" from r/WritingPrompts, r/memes, or satire sites for factual claims.
    4. Determine the verdict: TRUE, FALSE, MIXTURE, or UNVERIFIED.
    5. Provide a confidence score (0.0-1.0).
    6. Write a concise summary explaining your reasoning.
    
    Output format (JSON):
    {{
        "verdict": "TRUE" | "FALSE" | "MIXTURE" | "UNVERIFIED",
        "confidence": <float>,
        "summary": "<string>"
    }}
    """

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo", 
        "messages": [
            {"role": "system", "content": "You are a strict, logical fact-checker."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers) as resp:
                if resp.status != 200:
                    print(f"LLM Error: {await resp.text()}")
                    return None, 0.0, []
                result = await resp.json()
                content = result['choices'][0]['message']['content']
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(content)
                return parsed.get('verdict', 'UNVERIFIED').lower(), parsed.get('confidence', 0.5), [parsed.get('summary', '')]
    except Exception as e:
        print(f"LLM Exception: {e}")
        return None, 0.0, []

def filter_evidence(evidence):
    """
    Filters out known fiction/satire sources for the final display.
    """
    fiction_sources = ['r/WritingPrompts', 'r/memes', 'r/jokes', 'r/fakehistoryporn', 'r/aliens', 'r/conspiracy', 'The Onion', 'Babylon Bee']
    filtered = []
    for e in evidence:
        source = (e.get('source') or '').lower()
        link = (e.get('link') or '').lower()
        if any(fs.lower() in source for fs in fiction_sources) or any(fs.lower() in link for fs in fiction_sources):
            continue
        filtered.append(e)
    return filtered

async def verify_claim_text(text):
    # 1. Decompose
    queries = await decompose_claim(text)
    print(f"Decomposed '{text}' into: {queries}")
    
    # 2. Search (Parallel execution for sub-questions)
    all_evidence = []
    
    # Limit to top 2 queries to save API calls if needed, but 3 is fine
    for q in queries[:3]:
        # Run searches in parallel for this query
        results = await asyncio.gather(
            search_web(q),
            search_newsapi(q),
            search_reddit(q)
        )
        for r in results:
            all_evidence.extend(r)
            
    # Deduplicate evidence by link
    seen_links = set()
    unique_evidence = []
    for e in all_evidence:
        if e['link'] not in seen_links:
            unique_evidence.append(e)
            seen_links.add(e['link'])
    
    # 3. Verify
    # Try LLM first
    llm_verdict, llm_score, llm_reasons = await score_with_llm(text, unique_evidence)
    
    filtered_evidence = filter_evidence(unique_evidence)
    
    if llm_verdict:
        return {
            'verdict': llm_verdict,
            'score': llm_score,
            'evidence': filtered_evidence, # Return filtered evidence to user
            'reasons': llm_reasons,
            'summary': llm_reasons[0] if llm_reasons else "Verified by AI."
        }
        
    # Fallback (Simple Heuristic if LLM fails)
    # Re-using the logic from before but simplified as fallback
    return {
        'verdict': 'unverified',
        'score': 0.0,
        'evidence': filtered_evidence,
        'reasons': ["LLM verification unavailable."],
        'summary': "Could not verify claim due to system limitation."
    }

async def run_verifier(limit=50):
    cursor = claims.find({'status': 'unverified'}).limit(limit)
    updated = []
    async for c in cursor:
        text = c['text']
        result = await verify_claim_text(text)
        
        ver = {
            'claim_id': str(c['_id']),
            'verdict': result['verdict'],
            'score': result['score'],
            'evidence': result['evidence'],
            'checked_at': now_iso()
        }
        await verifications.insert_one(ver)
        await claims.update_one({'_id': c['_id']}, {'$set': {'status': result['verdict']}})
        updated.append(ver)
    return updated
