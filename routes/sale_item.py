from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db

router = APIRouter(prefix="/saleitem", tags=['Sale Items'])

@router.get('/')
def get_items(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 0, search: str | None = ""):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    items = db.query(models.SaleItem).filter(models.SaleItem.name.contains(search)).limit(limit).offset(skip).all()

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
def add_item(item: schemas.SaleItem, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    new_item = models.SaleItem(**item.dict(), creator=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put('/{id}')
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
    item_query.update(**item.dict(), creator=current_user.id, synchronize_session=False)
    return item_query.first()

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
    return Response(status_code=status.HTTP_204_NO_CONTENT)