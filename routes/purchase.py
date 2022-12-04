from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db

router = APIRouter(
    prefix="/purchase",
    tags=['Purchase']
)

@router.get('/')
def 