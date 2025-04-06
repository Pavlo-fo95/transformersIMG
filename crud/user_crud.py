from sqlalchemy.orm import Session
from models import user_models
from schemas import user_schemas
from utils.security import hash_password

# 🔐 Создание нового пользователя с хешированием пароля
def create_user(db: Session, user: user_schemas.UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 🔍 Получение пользователя по логину
def get_user_by_username(db: Session, username: str):
    return db.query(user_models.User).filter(user_models.User.username == username).first()

# 📋 Получение всех пользователей
def get_all_users(db: Session):
    return db.query(user_models.User).all()
