from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    email: str
    review: str
    service: str
    category: str

class CommentOut(CommentCreate):
    id: int
    date: datetime

    class Config:
        from_attributes = True

