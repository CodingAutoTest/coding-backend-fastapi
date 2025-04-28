from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.language import Language

async def get_language_id_by_name(db: AsyncSession, name: str) -> int:
    result = await db.execute(select(Language).where(Language.name == name))
    language = result.scalar_one_or_none()
    if not language:
        raise ValueError(f"존재하지 않는 언어: {name}")
    return language.language_id