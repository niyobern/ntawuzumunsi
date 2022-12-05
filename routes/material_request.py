from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/request", tags=["Material Request"])

@router.get('/')
def get_requests(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 10, search: Optional[str] = ""):
    if current_user.role.value not in ("kitchen", "store_keeper", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "No permission")
    requests = db.query(models.MaterialRequest).filter(models.MaterialRequest.tag.contains(search)).limit(limit).offset(skip).all()
    return requests

@router.get('/{id}')
def get_a_request(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("kitchen", "store_keeper", "manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    item = db.query(models.MaterialRequest).filter(models.MaterialRequest.id == id).first()
    return item 

@router.post('/')
def make_request(item: schemas.MaterialRequest, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "kitchen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    request = models.MaterialRequest(**item.dict(), creator=current_user.id)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

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
        else: request_query.update(found_request, accepted=True)
    return Response(status_code=status.HTTP_202_ACCEPTED, detail="done")


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
        else: request_query.update(found_query, accepted=False)



  
