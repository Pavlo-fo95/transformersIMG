from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
# from dotenv import load_dotenv
#
# load_dotenv()

# 📁 Путь к текущей директории (где находится файл database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📦 Путь к SQLite-базе данных
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'scantext.db')}"

# # 🌐 Подключение к Azure
# DATABASE_URL = os.getenv("AZURE_DB_URL")

# 🔌 Подключение к SQLite с параметром для многопоточности
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # обязательно для SQLite
)

# 🧠 Сессии для работы с БД
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🏛️ Базовый класс моделей
Base = declarative_base()
