import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .agents.fetcher import fetch_news
from .agents.claim_extractor import run_extractor
from .agents.verifier import run_verifier
from .db import init_indexes
from .config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

app = FastAPI(title='Misinfo Agentic API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix='/api')

@app.on_event('startup')
async def startup_event():
    await init_indexes()
    # start a scheduler to run agents periodically
    scheduler = AsyncIOScheduler()
    interval = int(settings.SCHED_RUN_INTERVAL_MIN)
    # fetch -> extract -> verify pipeline (staggered)
    scheduler.add_job(lambda: asyncio.create_task(fetch_news()), 'interval', minutes=interval, id='fetcher')
    scheduler.add_job(lambda: asyncio.create_task(run_extractor()), 'interval', minutes=interval, id='extractor', seconds=30)
    scheduler.add_job(lambda: asyncio.create_task(run_verifier()), 'interval', minutes=interval, id='verifier', seconds=60)
    scheduler.start()

@app.get('/')
async def root():
    return {'service': 'misinfo-agentic', 'version': '1.0'}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=settings.PORT, reload=True)
