from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ======= SCHEMAS =======

# 👤 Админ (базовый)
class AdminUserBase(BaseModel):
    email: str
    login: str
    subscription_status: Optional[bool] = False

# 👤 Админ (создание)
class AdminUserCreate(AdminUserBase):
    password: str

# 👤 Админ (ответ)
class AdminUserOut(AdminUserBase):
    id: int
    date_registration: datetime
    last_login_date: datetime

    class Config:
        from_attributes = True  # для pydantic v2

# 👤 Админ (вход)
class AdminLogin(BaseModel):
    login: str
    password: str

# 💳 Платеж (создание)
class PaymentCreate(BaseModel):
    user_id: int
    wallet_address: str
    amount: Optional[int] = None

# 💳 Платеж (ответ)
class PaymentOut(PaymentCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
