from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional

router = APIRouter(prefix="/sales", tags=['Sales'])

@router.get('/')
def get_sales(db: Session = Depends(get_db), current_user : schemas.User =Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 10, search: Optional[str] = ""):
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed to view this")
    sales = db.query(models.Sale).filter(models.Sale.tag.contains(search)).limit(limit).offset(skip).all()
    return sales

@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed to view this")
    item = db.query(models.Sale).filter(models.Sale.id == id).first()
    return item

@router.post('/')
def add_sale(item: schemas.Sale, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    new_item = models.Sale(**item.dict(), creator=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    sale_item = db.query(models.SaleItem).filter(models.SaleItem.id == item.item_id).first()
    price_per_item = sale_item.price
    total_price = price_per_item * item.quantity

    cash = models.Cash(label="sale_", amount=total_price, label_id = "sale_" + str(new_item.id), creator=current_user.id)
    db.add(cash)
    db.commit()
    db.refresh(cash)

    return new_item
