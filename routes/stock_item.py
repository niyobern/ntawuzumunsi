from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List

router = APIRouter(
    prefix="/stockitems",
    tags=['Stock Items']
)

@router.get('/')
def get_stock(db: Session = Depends(get_db), limit: int = 100, skip: int = 0, search: Optional[str] = "", start: str = "2022-12-18", end: str = "2023-12-30"):
    items = db.query(models.StockItem).filter(models.StockItem.created_at.between(start, end)).filter(models.StockItem.name.contains(search)).order_by(models.StockItem.created_at.desc()).limit(limit).offset(skip).all()
    items_info = []
    for item in items:
        item_info = {"id": item.id, "name": item.name, "price": item.price, "unit": item.unit, "description": item.description}
        items_info.append(item_info)
    return items_info

@router.get('/{id}')
def get_stock_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    item = db.query(models.StockItem).filter(models.StockItem.id == id).first() 
    return item   

@router.post('/')
def add_item(items: List[schemas.StockItem], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no priviledge")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    # item.creator = current_user.id
    for item in items:
        new_item = models.StockItem(**item.dict(), creator = current_user.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    return {"message": "created"}

@router.patch('/{id}')
def update_item(id: int, item: schemas.StockItem, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    item_query = db.query(models.StockItem).filter(models.StockItem.id == id)
    found_item = item_query.first()
    if found_item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if found_item.requisitions or found_item.material_request:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="can't be modified")
    itmeupdated = item.dic()
    itmeupdated["creator"] = current_user.id
    item_query.update(itmeupdated, synchronize_session=False) 
    db.commit()  
    return item

@router.delete('/{id}')
def delete_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    item_query = db.query(models.StockItem).filter(models.StockItem.id == id)
    found_item = item_query.first()
    item_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
