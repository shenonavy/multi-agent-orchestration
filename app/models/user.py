from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import Base

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String, default="user")

# Pydantic Models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    pass

class UserLogin(BaseModel):
    username: str
    password: str
