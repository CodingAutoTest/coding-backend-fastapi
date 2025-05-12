from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, BigInteger
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    pw = Column(String(255), nullable=False)
    premium_status = Column(Boolean, nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    last_login = Column(DateTime)
    solved_count = Column(Integer)
    rating = Column(BigInteger)
    profile_image = Column(String)
    background_image = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)
