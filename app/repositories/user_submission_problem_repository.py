from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_submission_problem import UserSubmissionProblem

async def save_submission(db: AsyncSession, submission: UserSubmissionProblem):
    db.add(submission)
    await db.commit()
    
async def has_user_solved(db, user_id: int, problem_id: int) -> bool:
    stmt = select(UserSubmissionProblem).where(
        UserSubmissionProblem.user_id == user_id,
        UserSubmissionProblem.problem_id == problem_id,
        UserSubmissionProblem.status == True
    ).limit(1)
    return (await db.execute(stmt)).scalars().first() is not None
