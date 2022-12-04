from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db

router = APIRouter(
    prefix="/purchase",
    tags=['Purchase']
)

@router.get('/')
def get_requisitions(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user),
  limit: int = 10, skip: int = 10, search: str | None = ""):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    items = db.query(models.Requisition).filter(models.Requisition.tag.contains(search)).limit(limit).offset(skip).all()
    return items

@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    item = db.query(models.Requisition).filter(models.Requisition.id == id).first()
    return item

@router.post('/')
def add_item(item : schemas.Requisition, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    
    new_item = models.Requisition(**item.dict(), creator=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put('/{id}')
def update_item(id: int, item: schemas.Requisition, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value == "no_role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "store_keeper"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough priviledge")
    item_query = db.query(models.Requisition).filter(models.Requisition.id == id)
    item_found = item_query.first()
    item_query.update(**item.dict(), creator=current_user.id)
    return item_query.first()
