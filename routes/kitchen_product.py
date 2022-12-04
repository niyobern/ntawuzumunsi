from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db

router = APIRouter(prefix="/kitchen", tags=["Kitchen Products"])

@router.get('/')
def get_products(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 10, search: str | None = ""):
    if current_user.role.value not in ("kitchen", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Notallowed to do this")
    products = db.query(models.KitchenProduct).filter(models.KitchenProduct.tag.contains(search)).limit(limit).offset(skip).all()
    return products

@router.get('/{id}')
def get_a_product(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("kitchen", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    product = db.query(models.KitchenProduct).filter(models.KitchenProduct.id == id).first()
    return product