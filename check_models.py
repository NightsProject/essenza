from app.services.model_registry import ModelRegistry
from app.config import get_settings
import asyncio

async def check():
    s = get_settings()
    r = ModelRegistry(s)
    await r.initialize()
    for mid, info in r.models.items():
        print(f'{mid}: loaded={info.loaded}, path={info.path}, error={info.error}')

asyncio.run(check())