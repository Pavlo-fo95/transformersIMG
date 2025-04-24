from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from datetime import datetime
from PIL import Image
import io
import pytesseract

from db.database import SessionLocal
from models.user_models import User, Upload
from schemas.user_schemas import UserLogin, UserOut, UserCreate, UploadOut, PasswordChange

from crud import user_crud
from utils.security import verify_password, hash_password

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
    user = user_crud.get_user_by_login(db, data.login)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Пароль успешно обновлён"}

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    print(f"Регистрация нового пользователя: {user.login}, {user.email}")

    if user_crud.get_user_by_login(db, user.login):
        print(f"Ошибка: Логин {user.login} уже используется.")
        raise HTTPException(status_code=400, detail="Логин уже используется")

    return user_crud.create_user(db, user)

@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/tesseract-ocr")
async def tesseract_ocr(
    file: UploadFile = File(...),
    lang: List[str] = Form(["eng"]),
    user_id: int = Form(...),  # 📌 теперь получаем user_id напрямую
    db: Session = Depends(get_db)
):
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        lang_code = '+'.join(lang)
        raw_text = pytesseract.image_to_string(image, lang=lang_code)
        text = raw_text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore').strip()

        user = db.query(User).filter_by(id=user_id).first()

        filename = f"tess_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
        path = f"uploads/{filename}"
        image.save(path)

        upload = Upload(
            filename=filename,
            uploaded_at=datetime.utcnow(),
            recognized_text=text,
            file_url=f"http://localhost:8000/uploads/{filename}",
            user_id=user.id if user else None,
            login=user.login if user else None
        )
        db.add(upload)
        db.commit()

        return {"text": text}
    except Exception as e:
        return {"error": f"Tesseract error: {str(e)}"}

# GET /uploads/by-login
@router.get("/uploads/by-login", response_model=List[UploadOut])
def get_uploads_by_login(login: str, db: Session = Depends(get_db)):
    print(f"🔍 login = {login}")
    user = db.query(User).filter_by(login=login).first()

    if not user:
        print("❌ Пользователь не найден")
        return []

    uploads = db.query(Upload).filter_by(user_id=user.id).order_by(Upload.uploaded_at.desc()).all()

    for u in uploads:
        if not u.file_url and u.filename:
            u.file_url = f"http://localhost:8000/uploads/{u.filename}"
        if u.recognized_text is None:
            u.recognized_text = ''

    print(f"📦 Найдено {len(uploads)} загрузок")
    return uploads
