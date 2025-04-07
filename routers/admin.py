from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal  # относительный импорт из того же уровня
from crud import admin_crud
from schemas import admin_schemas
from models import admin_models
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["Admin"])

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

# 📊 Получение статистики по загрузкам
@router.get("/{admin_id}/stats")
def get_admin_stats(admin_id: int, db: Session = Depends(get_db)):
    count = db.query(func.count(admin_models.Upload.id)).filter(admin_models.Upload.admin_id == admin_id).scalar()
    return {"upload_count": count}

@router.get("/all", response_model=list[admin_schemas.AdminUserOut])
def get_all_admins(db: Session = Depends(get_db)):
    return admin_crud.get_all_admins(db)