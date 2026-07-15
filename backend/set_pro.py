import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import get_settings

async def update_user():
    settings = get_settings()
    _db_url = settings.database_url.split("?")[0]
    _ssl_required = "sslmode=require" in settings.database_url or "neon.tech" in settings.database_url
    engine = create_async_engine(_db_url, connect_args={"ssl": "require"} if _ssl_required else {})
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE users SET plan='pro' WHERE email='selim@hsbvectoai.com'"))
    print("User selim@hsbvectoai.com updated to PRO plan for testing.")

asyncio.run(update_user())
