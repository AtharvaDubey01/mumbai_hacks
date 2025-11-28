# Verifier combines multiple signal sources:
# 1) Search for similar claim text via Google CSE or NewsAPI
# 2) Check fact-check APIs (if available)
# 3) Use an LLM to assess the claim against evidence

import aiohttp
from ..db import claims, verifications
from ..config import settings
from ..utils import now_iso
import asyncio

async def search_web(query):
    # Use Google Custom Search JSON API if available
    if settings.GOOGLE_CSE_API_KEY and settings.GOOGLE_CSE_ID:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': settings.GOOGLE_CSE_API_KEY, 'cx': settings.GOOGLE_CSE_ID, 'q': query, 'num': 5}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
        items = data.get('items', [])
        results = [{'title': i.get('title'), 'snippet': i.get('snippet'), 'link': i.get('link')} for i in items]
        return results
    # Fallback: empty
    return []

async def check_fact_check_apis(query):
    # placeholder for real fact-check API checks (e.g., Google Fact Check Tools)
    return []

async def score_with_llm(claim_text, evidence):
    # If OPENAI/HF key exists you would call the LLM here. We'll do a heuristic scoring.
    # Heuristics: if any evidence snippet contains 'fact-check' or 'false', lower score
    score = 0.5
    reasons = []
    for e in evidence:
        snippet = (e.get('snippet') or '').lower()
        if 'false' in snippet or 'not true' in snippet or 'misleading' in snippet:
            score -= 0.25
            reasons.append('evidence suggests false')
        if 'fact-check' in snippet or 'politi' in snippet or 'snopes' in snippet:
            score -= 0.2
            reasons.append('matched fact-check source')
    score = max(0.0, min(1.0, score))
    if score < 0.35:
        verdict = 'false'
    elif score < 0.6:
        verdict = 'mixture'
    else:
        verdict = 'unverified'
    return verdict, score, reasons

async def run_verifier(limit=50):
    cursor = claims.find({'status': 'unverified'}).limit(limit)
    updated = []
    async for c in cursor:
        text = c['text']
        evidence = await search_web(text)
        fc = await check_fact_check_apis(text)
        evidence += fc
        verdict, score, reasons = await score_with_llm(text, evidence)
        ver = {
            'claim_id': str(c['_id']),
            'verdict': verdict,
            'score': score,
            'evidence': evidence,
            'checked_at': now_iso()
        }
        await verifications.insert_one(ver)
        await claims.update_one({'_id': c['_id']}, {'$set': {'status': verdict}})
        updated.append(ver)
    return updated
