from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import pytesseract
import io
from pathlib import Path

from routers import user, admin
from db.database import SessionLocal
from crud import admin_crud
from schemas import admin_schemas
from models import admin_models, user_models

# Создание таблиц
admin_models.Base.metadata.create_all(bind=SessionLocal.kw["bind"])
user_models.Base.metadata.create_all(bind=SessionLocal.kw["bind"])

app = FastAPI()

@app.get("/")
def root():
    return {"message": "👋 Добро пожаловать в ScanText API"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно настроить конкретно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCR модель
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Подключение роутеров
app.include_router(user.router)
app.include_router(admin.router)

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

@app.post("/tesseract-ocr")
async def tesseract_ocr(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng, ru")
        return {"text": text.strip()}
    except Exception as e:
        return {"error": f"Tesseract error: {str(e)}"}

@app.get("/payments", response_model=list[admin_schemas.PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return admin_crud.get_payments(db)

# Удаление __pycache__ (опционально)
def delete_pycache_dirs(base_path):
    pycache_dirs = list(Path(base_path).rglob("__pycache__"))
    for dir_path in pycache_dirs:
        for file in dir_path.glob("*"):
            file.unlink()
        dir_path.rmdir()
    return len(pycache_dirs)

# delete_pycache_dirs(".")  # если запускать вручную