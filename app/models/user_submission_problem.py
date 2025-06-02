from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP, func
from app.db.database import Base

class UserSubmissionProblem(Base):
    __tablename__ = "user_submission_problem"

    user_submission_problem_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)
    execution_time = Column(DECIMAL(5, 2))
    memory_used = Column(Integer)
    status = Column(Integer)
    submission_code = Column(Text)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(String(255), nullable=True)
    ai_feedback_id = Column(Integer, ForeignKey("ai_feedback.ai_feedback_id"))
    language_id = Column(Integer, ForeignKey("language.language_id"))
    problem_id = Column(Integer, ForeignKey("problem.problem_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    passed_count = Column(Integer)
    total_count = Column(Integer)
    judge0_status = Column(Text)
    judge0_stderr = Column(Text)
    