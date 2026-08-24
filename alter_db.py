import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def alter_table():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(
                __import__('sqlalchemy').text("ALTER TABLE subscriptions ADD COLUMN status VARCHAR(50) DEFAULT 'unpaid'")
            )
        except Exception as e:
            print(e)
        try:
            await conn.execute(
                __import__('sqlalchemy').text("ALTER TABLE subscriptions ADD COLUMN payment_method VARCHAR(50)")
            )
        except Exception as e:
            print(e)
            
asyncio.run(alter_table())
