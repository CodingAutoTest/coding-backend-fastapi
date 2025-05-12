from app.models.problem import Problem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_problem_by_id(db: AsyncSession, problem_id: int) -> Problem:
    result = await db.execute(
        select(Problem).where(Problem.problem_id == problem_id)
    )
    return result.scalars().first()

async def save_problem(db: AsyncSession, problem: Problem):
    db.add(problem)
    await db.commit()