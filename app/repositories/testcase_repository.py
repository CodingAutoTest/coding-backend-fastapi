from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.testcase import Testcase

async def get_testcases_by_problem_id(
    db: AsyncSession, problem_id: int
) -> list[Testcase]:
    result = await db.execute(
        select(Testcase).where(Testcase.problem_id == problem_id).order_by(Testcase.testcase_id.asc())
    )
    return result.scalars().all()

async def get_testcase_by_id(db, testcase_id: int):
    result = await db.execute(
        select(Testcase).where(Testcase.testcase_id == testcase_id)
    )
    return result.scalars().first()
