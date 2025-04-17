from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminUserBase(BaseModel):
    email: str
    username: str
    subscription_status: Optional[bool] = False


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserOut(AdminUserBase):
    id: int
    date_registration: datetime
    last_login_date: datetime

    class Config:
        from_attributes = True

# 🔁 Краткая информация о пользователе
class UserShort(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# 💳 Платеж (создание)
class PaymentCreate(BaseModel):
    user_id: int
    amount: Optional[int] = None
    wallet_address: str
    reference: Optional[str] = None
    user_login: Optional[str] = None

# 💳 Платеж (ответ)
class PaymentOut(BaseModel):
    id: int
    amount: Optional[int]
    status: Optional[str]
    created_at: datetime
    wallet_address: str
    reference: Optional[str] = None
    user_login: Optional[str]
    user: UserShort

    class Config:
        from_attributes = True


