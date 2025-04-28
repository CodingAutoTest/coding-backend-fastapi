from sqlalchemy import Column, Integer, Text, String, ForeignKey, TIMESTAMP
from app.db.database import Base

class Testcase(Base):
    __tablename__ = "testcase"

    testcase_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    created_by = Column(String(255), nullable=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(String(255), nullable=True)
    problem_id = Column(Integer, ForeignKey("problem.id"), nullable=False)
