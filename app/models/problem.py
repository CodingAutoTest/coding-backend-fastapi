from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP
from app.db.database import Base

class Problem(Base):
    __tablename__ = "problem"

    problem_id = Column(Integer, primary_key=True, index=True)
    acceptance_rate = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    created_at = Column(TIMESTAMP, nullable=True)
    created_by = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, nullable=False)
    input_constraints = Column(Text, nullable=True)
    memory_limit = Column(Integer, nullable=False, default=256)
    output_constraints = Column(Text, nullable=True)
    time_limit = Column(DECIMAL(5, 2), nullable=False, default=2.00)
    title = Column(String(255), nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(String(255), nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    submission_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
