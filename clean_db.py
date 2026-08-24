import asyncio
from sqlalchemy.future import select
from sqlalchemy import delete
from models import Subscription
from database import AsyncSessionLocal

async def clean_db():
    async with AsyncSessionLocal() as session:
        # Get all subscriptions
        result = await session.execute(select(Subscription))
        subs = result.scalars().all()
        
        deleted_count = 0
        for sub in subs:
            if not sub.group_id.startswith("-"):
                print(f"Deleting private chat subscription: {sub.group_name} ({sub.group_id})")
                await session.execute(delete(Subscription).where(Subscription.id == sub.id))
                deleted_count += 1
                
        await session.commit()
        print(f"Cleanup complete. Deleted {deleted_count} private chat subscriptions.")

if __name__ == "__main__":
    asyncio.run(clean_db())
