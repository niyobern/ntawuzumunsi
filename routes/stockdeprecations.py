from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List

router = APIRouter(
    prefix="/stockdeprecation",
    tags=['Stock Deprecation']
)

@router.get('/')
def get_stockdeprecation(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), start: str = "2022-12-18", end: str = "2023-12-30",
  limit: int = 100, skip: int = 0, search: Optional[str] = ""):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    items = db.query(models.StockDeprecation).filter(models.StockDeprecation.created_at.between(start, end)).limit(limit).offset(skip).all()
    items_info = []
    for item in items:
        stock_item = db.query(models.StockItem).filter(models.StockItem.id == item.stock_id).first()
        created_time = str(item.created_at)
        info = {"id": item.id, "stock_id": stock_item.name, "quantity": item.quantity, "created_at": created_time[:10], "tag": item.tag}
        items_info.append(info)
    return items_info

@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    item = db.query(models.StockDeprecation).filter(models.StockDeprecation.id == id).first()
    return item

@router.post('/')
def add_item(items : List[schemas.StockDeprecation], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    
    for item in items:
        new_item = models.StockDeprecation(**item.dict(), creator=current_user.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    return {"message": "created"}

# @router.put('/{id}')
# def update_item(id: int, item: schemas.StockDeprecation, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
#     if current_user.role.value == "no_role":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
#     if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
#     item_query = db.query(models.StockDeprecation).filter(models.StockDeprecation.id == id)
#     item_found = item_query.first()
#     item_query.update(**item.dict(), creator=current_user.id)
#     return item_query.first()
