import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_table():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(
                __import__('sqlalchemy').text("UPDATE subscriptions SET status = 'active'")
            )
        except Exception as e:
            print(e)
            
asyncio.run(fix_table())
