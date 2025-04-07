from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

os.makedirs("db", exist_ok=True)
DATABASE_URL = "sqlite:///./db/scantext.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True)
    filename = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Integer)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False)
    review = Column(String(500), nullable=False)
    service = Column(String(100))
    category = Column(String(20), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if not db.query(User).first():
    db.add_all([
        User(username="user1", email="user1@example.com", password_hash="hash1"),
        User(username="user2", email="user2@example.com", password_hash="hash2"),
        User(username="user3", email="user3@example.com", password_hash="hash3"),
    ])

if not db.query(AdminUser).first():
    db.add(AdminUser(username="admin", email="admin@example.com", password_hash="adminhash"))

if not db.query(Upload).first():
    db.add_all([
        Upload(filename="scan1.jpg"),
        Upload(filename="scan2.jpg"),
    ])

if not db.query(Payment).first():
    db.add_all([
        Payment(user_id=1, amount=500, status="paid"),
        Payment(user_id=2, amount=300, status="pending"),
    ])

if not db.query(Comment).first():
    db.add_all([
        # positive
        Comment(email="happy_user1@example.com", review="Отличный сервис! Быстро и точно распознаёт текст с изображений.", service="ImageScanPro", category="positive", date=datetime(2025, 3, 28)),
        Comment(email="smiling_user2@example.com", review="Очень удобный инструмент. Работает без ошибок, рекомендую!", service="OCRMaster", category="positive", date=datetime(2025, 3, 27)),
        Comment(email="satisfied_client3@example.com", review="Лучший OCR-сервис, которым я пользовался!", service="QuickTextScan", category="positive", date=datetime(2025, 3, 26)),

        # neutral
        Comment(email="average_user1@example.com", review="Работает нормально, но бывают ошибки.", service="ImageScanPro", category="neutral", date=datetime(2025, 3, 28)),
        Comment(email="neutral_user2@example.com", review="Сервис выполняет свою функцию.", service="OCRMaster", category="neutral", date=datetime(2025, 3, 27)),
        Comment(email="just_user3@example.com", review="Обычный OCR-сервис.", service="QuickTextScan", category="neutral", date=datetime(2025, 3, 26)),

        # negative
        Comment(email="unhappy_user1@example.com", review="Очень низкое качество распознавания.", service="ImageScanPro", category="negative", date=datetime(2025, 3, 28)),
        Comment(email="angry_user2@example.com", review="Постоянно ошибки.", service="OCRMaster", category="negative", date=datetime(2025, 3, 27)),
        Comment(email="disappointed_client3@example.com", review="Разочарован. Деньги на ветер.", service="QuickTextScan", category="negative", date=datetime(2025, 3, 26)),
    ])

db.commit()
db.close()
print("✅ Данные успешно добавлены.")
