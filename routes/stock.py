from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List

router = APIRouter(
    prefix="/stock",
    tags=['Stock']
)

@router.get('/')
def get_stock(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 0, search: Optional[str] = "", start: str = "2022-12-18", end: str = "2023-12-30"):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "store_keeper", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    items = db.query(models.StockItem, models.Requisition).filter(models.Requisition.stock_id == models.StockItem.id).filter(models.StockItem.created_at.between(start, end)).filter(models.StockItem.name.contains(search)).limit(limit).offset(skip).all()
    # items_info = []
    # for item in items:
    #     info = {"Stock_id": item.id, "Price": item.price, "Quantity": item.quantity, "Unit": item.unit, "description": item.description}
    #     items_info.append(info)
    return items

@router.get('/{id}')
def get_stock_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    item = db.query(models.StockItem, models.Requisition).filter(models.StockItem.id == models.Requisition.stock_id == id).first() 
    return item   

