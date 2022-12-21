from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
import datetime
from typing import List
router = APIRouter(prefix="/saleitem", tags=['Sale Items'])

@router.get('/', response_model=schemas.SaleItemOut)
def get_items(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 0, search: Optional[str] = "", start: str = "2022-12-18", end: str = "2023-12-30"):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    items = db.query(models.SaleItem).filter(models.SaleItem.created_at.between(start, end)).filter(models.SaleItem.name.contains(search)).limit(limit).offset(skip).all()

    return items

@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    item = db.query(models.SaleItem).filter(models.SaleItem.id == id).first()
    return item

@router.post('/')
def add_item(items: List[schemas.SaleItem], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    for x in items:
        item = x.dict()
        item["creator"] = current_user.id
        new_item = models.SaleItem(**item)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    return {"message": "created"}

@router.patch('/{id}')
def update_item(id: int, item: schemas.SaleItem, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    item_query = db.query(models.SaleItem).filter(models.SaleItem.id == id)
    found_item = item_query.first()
    if found_item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    if found_item.sale or found_item.kitchen_product:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Can't me modified")
    item.creator = current_user.id
    item_query.update(item.dict(), synchronize_session=False)
    db.commit()
    return item

@router.delete('/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    item_query = db.query(models.SaleItem).filter(models.SaleItem.id == id)
    found_item = item_query.first()
    if found_item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    if found_item.sale or found_item.kitchen_product:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Can't me modified")

    item_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)