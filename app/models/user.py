from sqlalchemy import Column, Integer
from app.db.database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
