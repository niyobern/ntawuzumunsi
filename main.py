from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import models
from database.database import get_db
from utils.schemas import User
from routes import user, auth

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)

@app.post('/')
def index(user_info: User, db: Session = Depends(get_db)):
    user = models.User(**user_info.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

