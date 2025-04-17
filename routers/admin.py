from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime

from db.database import SessionLocal
from crud import admin_crud
from schemas import admin_schemas
from models import admin_models
from models.admin_models import AdminUser
from utils.security import verify_password

router = APIRouter()

# 📦 Получить доступ к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Создание администратора
@router.post("/create", response_model=admin_schemas.AdminUserOut)
def create_admin(admin: admin_schemas.AdminUserCreate, db: Session = Depends(get_db)):
    return admin_crud.create_admin_user(db, admin)


# 🔐 Авторизация администратора
@router.post("/login", response_model=admin_schemas.AdminUserOut)
def login_admin(credentials: admin_schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = admin_crud.get_admin_user_by_username(db, credentials.username)
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return admin


# 📋 Все админы
@router.get("/all", response_model=list[admin_schemas.AdminUserOut])
def get_all_admins(db: Session = Depends(get_db)):
    return admin_crud.get_all_admins(db)


# 📊 Статистика загрузок
@router.get("/{admin_id}/stats")
def get_admin_stats(admin_id: int, db: Session = Depends(get_db)):
    count = db.query(func.count(admin_models.Upload.id)) \
              .filter(admin_models.Upload.admin_id == admin_id) \
              .scalar()
    return {"upload_count": count}


# 📋 Все платежи
@router.get("/payments/", response_model=list[admin_schemas.PaymentOut])
def get_payments(db: Session = Depends(get_db)):
    return (
        db.query(admin_models.Payment)
        .options(joinedload(admin_models.Payment.user))
        .all()
    )


# 💳 Создание платежа
@router.post("/payments/create", response_model=admin_schemas.PaymentOut)
def create_payment(payment: admin_schemas.PaymentCreate, db: Session = Depends(get_db)):
    db_payment = admin_models.Payment(
        user_id=payment.user_id,
        wallet_address=payment.wallet_address,
        amount=payment.amount,
        reference=payment.reference,
        user_login=payment.user_login,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


# 🔄 Обновление статуса вручную
@router.patch("/payments/{payment_id}/status")
def update_payment_status(payment_id: int, status: str, db: Session = Depends(get_db)):
    payment = db.query(admin_models.Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")
    payment.status = status
    db.commit()
    db.refresh(payment)
    return {"message": "Статус обновлён", "payment": payment}


# 🤖 Обновление статуса через Monobank callback
@router.post("/payments/callback")
def monobank_callback(payload: dict, db: Session = Depends(get_db)):
    reference = payload.get("reference")
    status = payload.get("status")

    if not reference:
        raise HTTPException(status_code=400, detail="reference отсутствует")

    payment = db.query(admin_models.Payment).filter_by(reference=reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")

    payment.status = status
    db.commit()
    return {"message": "Статус платежа обновлён"}


# 👤 Платежи по логину пользователя (админский просмотр)
@router.get("/admin/payments/by-user", response_model=list[admin_schemas.PaymentOut])
def get_user_payments(login: str, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter_by(login=login).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.payments
