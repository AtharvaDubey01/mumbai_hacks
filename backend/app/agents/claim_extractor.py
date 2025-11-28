# This module extracts candidate claims from raw items using a small LLM or a heuristics pipeline.

from transformers import pipeline
from ..db import raw_items, claims
from ..utils import now_iso
import os
from ..config import settings
import asyncio

# For production, use a more advanced claim-extraction model. Here we use a text2text pipeline prompt.
# If OPENAI_API_KEY is provided you can call OpenAI or use a hosted HF model.

# Fallback: simple heuristics extractor

async def extract_from_text(text: str):
    # simple sentence-based heuristics: short assertive sentences with keywords
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    candidates = []
    keywords = ['cause', 'prevent', 'cure', 'vaccine', 'ban', 'laws', 'immediately', 'proven', 'study', 'research']
    for s in sentences:
        if len(s.split()) < 5 or len(s.split()) > 40:
            continue
        if any(k in s.lower() for k in keywords):
            candidates.append(s)
    return candidates

async def run_extractor(limit=50):
    cursor = raw_items.find().sort('fetched_at', -1).limit(limit)
    created = []
    async for item in cursor:
        full_text = item.get('meta', {}).get('full_text') or item.get('summary') or item.get('title')
        if not full_text:
            continue
        candidates = await extract_from_text(full_text)
        for c in candidates:
            claim_doc = {
                'raw_id': str(item['_id']),
                'text': c,
                'extracted_at': now_iso(),
                'status': 'unverified'
            }
            res = await claims.insert_one(claim_doc)
            claim_doc['_id'] = str(res.inserted_id)
            created.append(claim_doc)
    return created
