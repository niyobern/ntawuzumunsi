from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
import datetime
from typing import List

router = APIRouter(prefix='/eservices', tags=["E-Services"])

@router.get('/')
def get_services(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 100, skip: int = 10, start: str = "2022-12-18", end: str = datetime.datetime.now().date()):
    if current_user.role.value not in ("manager", "boss", "eservices"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    services = db.query(models.Eservice).filter(models.Eservice.created_at.between(start, end)).limit(limit).offset(skip).order_by(models.Cash.created_at.desc()).all()
    return services

@router.post('/')
def post_service(items: List[schemas.Eservice], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), start: str = "2022-12-18", end: str = "2023-12-30"):
    if current_user.role.value != "eservices":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are not authorised to do this")
    for item in items:
        service = models.Eservice(**item.dict(), creator=current_user.id)
        db.add(service)
        db.commit()
        db.refresh(service)
    
        cash = models.Cash(label="eservice_", amount=item.price, label_id = "eservice_" + str(service.id), creator=current_user.id)
        db.add(cash)
        db.commit()
        db.refresh(cash)

    return {"message": "created"}