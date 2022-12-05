from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
router = APIRouter(prefix='/eservices', tags=["E-Services"])

@router.get('/')
def get_services(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 10):
    if current_user.role.value not in ("manager", "boss", "eservices"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    services = db.query(models.Eservice).limit(limit).offset(skip).all()
    return services

@router.post('/')
def post_service(item: schemas.Eservice, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value != "eservices":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are not authorised to do this")
    service = models.Eservice(**item.dict(), creator=current_user.id)
    db.add(service)
    db.commit()
    db.refresh(service)

    cash = models.Cash(label="eservice_", amount=item.price, label_id = "eservice_" + str(service.id), creator=current_user.id)
    db.add(cash)
    db.commit()
    db.refresh(cash)

    return service