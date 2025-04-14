from sqlalchemy.orm import Session
from models import user_models
from schemas.user_schemas import UserLogin, UserOut, UserCreate
from utils.security import hash_password
from models.user_models import User

# 🔐 Создание нового пользователя с хешированием пароля
def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = user_models.User(
        login=user.login,
        email=user.email,
        password_hash=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_login(db: Session, login: str):
    return db.query(user_models.User).filter(user_models.User.login == login).first()

def get_all_users(db: Session):
    return db.query(user_models.User).all()
