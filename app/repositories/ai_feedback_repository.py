from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.ai_feedback import AiFeedback

async def save_feedback(db: AsyncSession, feedback: AiFeedback):
    db.add(feedback)
    await db.flush() 