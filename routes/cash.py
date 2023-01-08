from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
import datetime

router = APIRouter(prefix='/cash', tags=["Cash"])

@router.get('/all')
def get_transactions(db: Session = Depends(get_db), current_user: schemas.User = Depends(
    oauth2.get_current_user), limit: int = 100, skip: int = 0, start: str = "2022-12-18", end: str = "2023-12-30"):
    if current_user.role.value not in ("manager", "boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    cashflow = db.query(models.Cash).filter(models.Cash.created_at.between(start, end)).limit(limit).offset(skip).all()
    income = 0
    expenditures = 0
    for item in cashflow:
        creator = db.query(models.User).filter(models.User.id == item.creator).first()
        item.creator = creator.name.split()[0]
        if item.label.value != "purchase":
            income += item.amount
        else: expenditures += item.amount
    result = {"cashflow": cashflow, "income": income, "expenditures": expenditures}
    return result