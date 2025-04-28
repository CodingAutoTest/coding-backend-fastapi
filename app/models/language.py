from sqlalchemy import Column, Integer, Text, String, ForeignKey, TIMESTAMP
from app.db.database import Base

class Language(Base):
    __tablename__ = "language"

    language_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)

