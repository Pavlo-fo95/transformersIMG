from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    login: str
    email: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    login: str
    email: str
    registered_at: datetime
    role: Optional[str] = "user"

    class Config:
        from_attributes = True
