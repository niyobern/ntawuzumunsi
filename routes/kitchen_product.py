from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List

router = APIRouter(prefix="/kitchen", tags=["Kitchen Products"])

@router.get('/')
def get_products(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 10, search: Optional[str] = "", start: str = "2022-12-18", end: str = datetime.datetime.now().date()):
    if current_user.role.value not in ("kitchen", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Notallowed to do this")
    products = db.query(models.KitchenProduct).filter(models.Cash.created_at.between(start, end)).filter(models.KitchenProduct.name.contains(search)).limit(limit).offset(skip).all()
    return products

@router.get('/{id}')
def get_a_product(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("kitchen", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    product = db.query(models.KitchenProduct).filter(models.KitchenProduct.id == id).first()
    return product

@router.post('/')
def add_item(items: List[schemas.KitchenProduct], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "kitchen":
        raise HTTPException(status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail="You don't work in kitchen")
    for item in items:   
        product = models.KitchenProduct(**item.dict(), creator=current_user.id)
        db.add(product)
        db.commit()
        db.refresh(product)
    return {"message": "created"}