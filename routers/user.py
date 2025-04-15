from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from crud import user_crud
from schemas.user_schemas import UserLogin, UserOut, UserCreate
from db.database import SessionLocal
from utils.security import verify_password, hash_password
from models.user_models import User
from schemas.user_schemas import PasswordChange

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
    try:
        db_user = user_crud.get_user_by_login(db, user.login)
        if not db_user or not verify_password(user.password, db_user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        return db_user
    except Exception as e:
        print("❌ Ошибка при входе:", e)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/change-password")
def change_password(data: PasswordChange, db: Session = Depends(get_db)):
    # Получаем пользователя по логину
    user = user_crud.get_user_by_login(db, data.login)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем старый пароль
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    # Обновляем пароль
    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Пароль успешно обновлён"}

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Логирование для проверки входных данных
    print(f"Регистрация нового пользователя: {user.login}, {user.email}")

    # Проверка на уникальность логина
    if user_crud.get_user_by_login(db, user.login):
        print(f"Ошибка: Логин {user.login} уже используется.")
        raise HTTPException(status_code=400, detail="Логин уже используется")

    return user_crud.create_user(db, user)

# 📋 Получить всех пользователей (используется в React)
@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
