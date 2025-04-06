from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from crud import user_crud
from schemas import user_schemas
from db.database import SessionLocal


router = APIRouter(prefix="/user", tags=["User"])

# 💾 Получить доступ к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Регистрация нового пользователя
@router.post("/register", response_model=user_schemas.UserOut)
def register_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)

# 🔍 Получить пользователя по логину
@router.get("/{username}", response_model=user_schemas.UserOut)
def get_user(username: str, db: Session = Depends(get_db)):
    return user_crud.get_user_by_username(db, username)

# 📋 Получить всех пользователей
@router.get("/", response_model=list[user_schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return user_crud.get_all_users(db)
