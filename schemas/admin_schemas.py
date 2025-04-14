from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ======= SCHEMAS =======
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
