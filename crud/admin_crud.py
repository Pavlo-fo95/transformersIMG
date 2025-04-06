from sqlalchemy.orm import Session
from schemas import admin_schemas
from models import admin_models
from utils.security import hash_password

# 🔐 Создание администратора с хешированием пароля
def create_admin_user(db: Session, admin: admin_schemas.AdminUserCreate):
    hashed_pw = hash_password(admin.password)
    db_admin = admin_models.AdminUser(
        email=admin.email,
        login=admin.login,
        password_hash=hashed_pw,
        subscription_status=admin.subscription_status
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# 🔎 Поиск по логину
def get_admin_user_by_login(db: Session, login: str):
    return db.query(admin_models.AdminUser).filter(admin_models.AdminUser.login == login).first()

# 📋 Все админы
def get_all_admins(db: Session):
    return db.query(admin_models.AdminUser).all()

# 💸 Создание платежа
def create_payment(db: Session, payment: admin_schemas.PaymentCreate):
    db_payment = admin_models.Payment(
        user_id=payment.user_id,
        amount=payment.amount,
        wallet_address=payment.wallet_address
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# 📋 Все платежи
def get_payments(db: Session):
    return db.query(admin_models.Payment).all()

# 📋 Платежи конкретного пользователя
def get_payments_by_user_id(db: Session, user_id: int):
    return db.query(admin_models.Payment).filter(admin_models.Payment.user_id == user_id).all()
