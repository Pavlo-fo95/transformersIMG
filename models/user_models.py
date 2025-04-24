from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    role = Column(String(50), default="user")

    uploads = relationship("Upload", back_populates="user")  # 👈 связь с Upload


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ✅ здесь связь
    recognized_text = Column(Text, nullable=True)
    file_url = Column(Text, nullable=True)

    user = relationship("User", back_populates="uploads")  # ✅ связь обратно
