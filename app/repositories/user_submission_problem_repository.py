from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_submission_problem import UserSubmissionProblem

async def save_submission(db: AsyncSession, submission: UserSubmissionProblem):
    db.add(submission)
    await db.commit()