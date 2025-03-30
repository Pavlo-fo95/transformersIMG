from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import io

app = FastAPI()

# Настройка CORS для фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # конкретный домен фронта https://scantext.z36.web.core.windows.net
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка модели и процессора один раз при старте
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Предобработка изображения
        pixel_values = processor(images=image, return_tensors="pt").pixel_values

        # Генерация текста
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return {"text": text}

    except Exception as e:
        return {"error": f"Ошибка обработки изображения: {str(e)}"}
