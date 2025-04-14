from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    date_registration = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, default=datetime.utcnow)
    subscription_status = Column(Boolean, default=False)


    # Это для обратной связи
    uploads = relationship("Upload", back_populates="admin")

    payments = relationship("Payment", back_populates="user")

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Вот тут foreign key к администратору
    admin_id = Column(Integer, ForeignKey("admin_users.id"))

    # Это удобно для ORM
    admin = relationship("AdminUser", back_populates="uploads")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    wallet_address = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("AdminUser", back_populates="payments")

