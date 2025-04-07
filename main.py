from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import pytesseract
import io
from pathlib import Path
from dotenv import load_dotenv
import os

# 🔗 Импорт модулей проекта
from routers import user, admin, comment
from db.database import SessionLocal
from crud import admin_crud
from schemas import admin_schemas
from models import admin_models, user_models, comment_models

# 🔄 Загрузка переменных окружения (.env)
load_dotenv()

# 🔨 Создание таблиц в БД
admin_models.Base.metadata.create_all(bind=SessionLocal.kw["bind"])
user_models.Base.metadata.create_all(bind=SessionLocal.kw["bind"])
comment_models.Base.metadata.create_all(bind=SessionLocal.kw["bind"])

# 🧠 Инициализация FastAPI
app = FastAPI()

# ✅ Разрешаем доступ с React (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React Dev
        "http://127.0.0.1:3000",     # React Dev альтернативный
        "https://scantext.z36.web.core.windows.net",  # Продакшн
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 OCR-модель
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

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

# 🖼 Распознавание текста (TrOCR)
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return {"text": text}
    except Exception as e:
        return {"error": f"TrOCR error: {str(e)}"}

# 🖼 Распознавание текста (Tesseract)
@app.post("/tesseract-ocr")
async def tesseract_ocr(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng,ru")
        return {"text": text.strip()}
    except Exception as e:
        return {"error": f"Tesseract error: {str(e)}"}

# 🔘 Тестовый корневой эндпоинт
@app.get("/")
def root():
    return {"message": "👋 Добро пожаловать в ScanText API"}

# 🧪 Тест подключения к БД
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    users = db.query(user_models.User).all()
    return {"user_count": len(users)}

# 📄 Список платежей (для админки)
@app.get("/payments", response_model=list[admin_schemas.PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return admin_crud.get_payments(db)

# 🧹 Удаление __pycache__ (опционально)
def delete_pycache_dirs(base_path):
    pycache_dirs = list(Path(base_path).rglob("__pycache__"))
    for dir_path in pycache_dirs:
        for file in dir_path.glob("*"):
            file.unlink()
        dir_path.rmdir()
    return len(pycache_dirs)

# delete_pycache_dirs(".")  # 👉 если надо вручную чистить
