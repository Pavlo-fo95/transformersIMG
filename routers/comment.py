from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from schemas.comment_schemas import CommentCreate, CommentOut
from crud import comment_crud

router = APIRouter(prefix="/comments", tags=["Comments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CommentOut)
def create(comment: CommentCreate, db: Session = Depends(get_db)):
    return comment_crud.create_comment(db, comment)

@router.get("/", response_model=List[CommentOut])
def get_all(db: Session = Depends(get_db)):
    return comment_crud.get_all_comments(db)

@router.get("/category/{category}", response_model=List[CommentOut])
def get_by_category(category: str, db: Session = Depends(get_db)):
    return comment_crud.get_comments_by_category(db, category)
