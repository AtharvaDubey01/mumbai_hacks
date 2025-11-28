from fastapi import APIRouter, Depends, HTTPException
from ..db import raw_items, claims, verifications
from ..utils import now_iso
from bson import ObjectId
from typing import List

router = APIRouter()

@router.get('/health')
async def health():
    return {'status': 'ok'}

@router.get('/items')
async def get_items(limit: int = 50):
    cursor = raw_items.find().sort('fetched_at', -1).limit(limit)
    items = [item async for item in cursor]
    for i in items:
        i['_id'] = str(i['_id'])
    return items

@router.get('/claims')
async def get_claims(limit: int = 50):
    cursor = claims.find().sort('extracted_at', -1).limit(limit)
    result = [c async for c in cursor]
    for c in result:
        c['_id'] = str(c['_id'])
    return result

@router.get('/verifications')
async def get_verifications(limit: int = 50):
    cursor = verifications.find().sort('checked_at', -1).limit(limit)
    result = [v async for v in cursor]
    for v in result:
        v['_id'] = str(v['_id'])
    return result

@router.post('/verify/{claim_id}')
async def manual_verify(claim_id: str):
    # This can call the verifier logic directly
    claim = await claims.find_one({'_id': ObjectId(claim_id)})
    if not claim:
        raise HTTPException(404, 'Claim not found')
    # placeholder: set status
    await claims.update_one({'_id': ObjectId(claim_id)}, {'$set': {'status': 'queued_for_manual'}})
    return {'ok': True}
