from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional


router = APIRouter(prefix="/links", tags=['Links'])

@router.get('/')
def get_links(db: Session = Depends(get_db), current_user : schemas.User =Depends(oauth2.get_current_user)):
    role = current_user.role.value
    if role in ["manager", "boss", "deputy_boss"]:
        links = ["purchases", "sales", "users", "stock", "products", "requests", "kitchen", "cash", "eservices"]
        return links
    elif role == "store_keeeper":
        links = ["purchases", "stock", "requests"]
        return links
    elif role == "retailer":
        links = ["sales", "products"]
        return links
    elif role == "eservices":
        links = ["eservices"]
        return links