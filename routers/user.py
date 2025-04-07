# routers/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from crud import user_crud
from schemas.user_schemas import UserLogin, UserOut
from db.database import SessionLocal
from utils.security import verify_password
from models.user_models import User

router = APIRouter()

# 🔌 Подключение к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔐 Вход пользователя
@router.post("/login", response_model=UserOut)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return db_user

# 📋 Получить всех пользователей (используется в React)
@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
