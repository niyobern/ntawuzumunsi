from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import List, Optional
import datetime
from typing import List

router = APIRouter(prefix="/request", tags=["Material Request"])

@router.get('/')
def get_requests(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), 
  limit: int = 100, skip: int = 0, search: Optional[str] = "", start: str = "2022-12-18", end: str = "2023-12-30"):
    if current_user.role.value not in ("kitchen", "store_keeper", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "No permission")
    requests = db.query(models.MaterialRequest).filter(models.MaterialRequest.accepted == None).filter(models.MaterialRequest.created_at.between(start, end)).filter(models.MaterialRequest.tag.contains(search)).order_by(models.MaterialRequest.created_at.desc()).limit(limit).offset(skip).all()
    requests_list = []
    for request in requests:
        creator = db.query(models.User).filter(models.User.id == request.creator).first()
        material = db.query(models.StockItem).filter(models.StockItem.id == request.item_id).first()
        item = {"Id": request.id, "item_id": material.name, "Quantity": request.quantity, "Creator": creator.name, "accepted": request.accepted} 
        requests_list.append(item)
    return requests_list

@router.get('/{id}')
def get_a_request(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("kitchen", "store_keeper", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    item = db.query(models.MaterialRequest).filter(models.MaterialRequest.id == id).first()
    return item 

@router.post('/')
def make_request(items: List[schemas.MaterialRequest], db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "kitchen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    for item in items:
        request = models.MaterialRequest(**item.dict(), creator=current_user.id)
        db.add(request)
        db.commit()
        db.refresh(request)
    return {"message": "created"}

@router.post('/accept')
def accept_request(ids: List[int], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "store_keeper":
        raise HTTPException(status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail="Not a store_keeper")
    for id in ids:
        request_query = db.query(models.MaterialRequest).filter(models.MaterialRequest.id == id)
        found_request = request_query.first()
        if found_request == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
        if found_request.accepted == False:
            return HTTPException(status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail=f"{id} the request have been declined, so it can't be edited")
        elif found_request.accepted == True:
            return HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"{id} already accepted")
        request_query.update({"accepted": True}, synchronize_session=False)
        db.commit()
    return {"message": "done"}

@router.post('/deny')
def deny_request(ids: List[int], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "store_keeper":
        raise HTTPException(status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail="Not allowed")
    for id in ids:
        request_query = db.query(models.MaterialRequest).filter(models.MaterialRequest.id == id)
        found_query = request_query.first()
        if found_query == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
        if found_query.accepted == True:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"{id} has been accepted before")
        elif found_query.accepted == False:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"{id} has beeen already declined")
        request_query.update({"accepted": True}, synchronize_session=False)
        db.commit()
    return {"message": "done"}


  
