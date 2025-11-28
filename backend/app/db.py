import motor.motor_asyncio
from .config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_default_database()

# Collections
raw_items = db['raw_items']
claims = db['claims']
verifications = db['verifications']

async def init_indexes():
    await raw_items.create_index('fetched_at')
    await claims.create_index('status')
    await verifications.create_index('claim_id')
