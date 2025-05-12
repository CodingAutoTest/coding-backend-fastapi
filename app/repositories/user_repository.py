from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

async def save_user(db: AsyncSession, user: User):
    db.add(user)
    await db.commit()
    
async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalars().first()