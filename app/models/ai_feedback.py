from sqlalchemy import Column, Integer, Text
from app.db.database import Base

class AiFeedback(Base):
    __tablename__ = "ai_feedback"

    ai_feedback_id = Column(Integer, primary_key=True, index=True)
    accuracy = Column(Integer)
    efficiency = Column(Integer)
    feedback = Column(Text)
    readability = Column(Integer)
    test_coverage = Column(Integer)