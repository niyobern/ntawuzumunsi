from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db

router = APIRouter(
    prefix="/stockitems",
    tags=['Stock Items']
)

@router.get('/')
def get_stock(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 0, search: str | None = ""):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "store_keeper", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    items = db.query(models.StockItem).filter(models.StockItem.name.contains(search)).limit(limit).offset(skip).all()

    return items

@router.get('/{id}')
def get_stock_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    item = db.query(models.StockItem).filter(models.StockItem.id == id).first() 
    return item   

@router.post('/')
def add_item(item: schemas.StockItem, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no priviledge")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    # item.creator = current_user.id
    new_item = models.StockItem(**item.dict(), creator = current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put('/{id}')
def update_item(id: int, item: schemas.StockItem, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    item_query = db.query(models.StockItem).filter(models.StockItem.id == id)
    found_item = item_query.first()
    if found_item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if found_item.requisition or found_item.material_request:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="can't be modified")
    item_query.update(**item.dict(), synchronize_session=False) 
    db.commit()  
    return item_query.first()

@router.delete('/{id}')
def delete_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have no priviledge to view this")
    if current_user.role.value not in ("boss", "deputy_boss", "manager", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed") 
    item_query = db.query(models.StockItem).filter(models.StockItem.id == id)
    found_item = item_query.first()
    item_query.delete(synchronize_session=False)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
