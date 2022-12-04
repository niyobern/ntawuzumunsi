from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import models
from database.database import get_db
from utils.schemas import User


app = FastAPI()

@app.post('/')
def index(user_info: User, db: Session = Depends(get_db)):
    user = models.User(**user_info.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

