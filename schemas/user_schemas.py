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

class PasswordChange(BaseModel):
    login: str
    old_password: str
    new_password: str

class UserOut(BaseModel):
    id: int
    login: str
    email: str
    registered_at: datetime
    role: Optional[str] = "user"

    class Config:
        from_attributes = True

class UploadOut(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    user_id: Optional[int]
    login: Optional[str]
    recognized_text: Optional[str] = None
    file_url: Optional[str] = None

    class Config:
        from_attributes = True