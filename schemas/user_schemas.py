from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 🧾 Базовая схема пользователя
class UserBase(BaseModel):
    username: str
    email: str

# 🆕 Схема для создания пользователя
class UserCreate(UserBase):
    password: str

# 📤 Схема ответа
class UserOut(UserBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True  # для поддержки ORM-моделей
