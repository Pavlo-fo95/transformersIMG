import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from typing import Optional, List
from PIL import Image
import pytesseract
import io
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# 🔗 Импорт модулей проекта
from routers import user, admin, comment
from db.database import SessionLocal, engine
from crud import admin_crud
from schemas import admin_schemas
from models import admin_models, user_models, comment_models
from models.user_models import Upload, User

# 🔄 Загрузка переменных окружения (.env)
load_dotenv()

# OCR модель
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

# 🔨 Создание таблиц в БД
admin_models.Base.metadata.create_all(bind=engine)
user_models.Base.metadata.create_all(bind=engine)
comment_models.Base.metadata.create_all(bind=engine)

# 🧠 Инициализация FastAPI
app = FastAPI()

# ✅ Разрешаем доступ с React (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://scantext.z36.web.core.windows.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚙️ Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🚀 Подключение маршрутов
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(comment.router, prefix="/comments", tags=["Comments"])

# Раздача загруженных файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ✅ Общая функция для сохранения распознанного файла
def save_upload_to_db(db: Session, text: str, image: Image.Image, user: Optional[User] = None) -> Upload:
    os.makedirs("uploads", exist_ok=True)
    filename = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join("uploads", filename)
    image.save(filepath)

    upload = Upload(
        filename=filename,
        uploaded_at=datetime.utcnow(),
        recognized_text=text,
        file_url=f"http://localhost:8000/uploads/{filename}",
        user_id=user.id if user else None
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


# 🧠 TrOCR модель
@app.post("/extract-text")
async def extract_text(
    file: UploadFile = File(...),
    login: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        user = db.query(User).filter_by(login=login).first() if login else None
        upload = save_upload_to_db(db, text, image, user)
        return {"text": text, "file_url": upload.file_url}
    except Exception as e:
        return {"error": f"TrOCR error: {str(e)}"}

# 🔘 Корневой тест
@app.get("/")
def root():
    return {"message": "👋 Добро пожаловать в ScanText API"}

# 🧪 Тест подключения к БД
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    users = db.query(user_models.User).all()
    return {"user_count": len(users)}

# 🧹 Удаление __pycache__ (по желанию)
def delete_pycache_dirs(base_path):
    pycache_dirs = list(Path(base_path).rglob("__pycache__"))
    for dir_path in pycache_dirs:
        for file in dir_path.glob("*"):
            file.unlink()
        dir_path.rmdir()
    return len(pycache_dirs)

# delete_pycache_dirs(".")
