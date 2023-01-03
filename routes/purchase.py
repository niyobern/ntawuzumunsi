from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List

router = APIRouter(
    prefix="/purchase",
    tags=['Purchase']
)

@router.get('/')
def get_requisitions(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), start: str = "2022-12-18", end: str = "2023-12-30",
  limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    items = db.query(models.Requisition).filter(models.Requisition.created_at.between(start, end)).limit(limit).offset(skip).all()
    items_info = []
    for item in items:
        created_time = str(item.created_at)
        info = {"id": item.id, "stock_id": item.stock_id, "quantity": item.quantity, "created_at": created_time[:10], "tag": item.tag}
    return items_info

@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    item = db.query(models.Requisition).filter(models.Requisition.id == id).first()
    return item

@router.post('/')
def add_item(items : List[schemas.Requisition], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    
    for item in items:
        new_item = models.Requisition(**item.dict(), creator=current_user.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    
        stock_item = db.query(models.StockItem).filter(models.StockItem.id == item.stock_id).first()
        price_per_item = stock_item.price
        total_price = price_per_item * item.quantity
    
        cash = models.Cash(label="purchase", amount=total_price*(-1), label_id = "purchase" + str(new_item.id), creator=current_user.id)
        db.add(cash)
        db.commit()
        db.refresh(cash)

    return {"message": "created"}

# @router.put('/{id}')
# def update_item(id: int, item: schemas.Requisition, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
#     if current_user.role.value == "no_role":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
#     if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
#     item_query = db.query(models.Requisition).filter(models.Requisition.id == id)
#     item_found = item_query.first()
#     item_query.update(**item.dict(), creator=current_user.id)
#     return item_query.first()
