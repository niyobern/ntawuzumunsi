from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
from datetime import datetime  
from datetime import timedelta  
from typing import List

router = APIRouter(prefix="/sales", tags=['Sales'])

@router.get('/')
def get_summary(db: Session = Depends(get_db), current_user : schemas.User =Depends(oauth2.get_current_user)):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    results = []
    if current_user.role.value in ("manager", "boss", "deputy_boss", "retailer"):
        sales = db.query(models.Sale, models.SaleItem).filter(models.Sale.item_id == models.SaleItem.id).filter(models.KitchenProduct.created_at.between(start, end)).all()
        purchases_values = [x.price for x in sales]
        value = sum(purchases_values)
        sales_count = len(sales)
        results.append({"sales_count": sales_count, "sales_value": value})
    if current_user.role.value in ("manager", "boss", "deputy_boss", "store_keeper"):
        purchases = db.query(models.Requisition, models.StockItem).filter(models.StockItem.id == models.Requisition.stock_id).filter(models.Requisition.created_at.between(start, end)).all()
        purchases_count = len(purchases)
        values = [x.price for x in purchases]
        value = sum(values)
        results.append({"purchases_count": purchases_count, "purchases_value": value})
    return results


@router.get('/{id}')
def get_item(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed to view this")
    item = db.query(models.Sale).filter(models.Sale.id == id).first()
    return item

@router.post('/')
def add_sale(items: List[schemas.Sale], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    for item in items:
        new_item = models.Sale(**item.dict(), creator=current_user.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        sale_item = db.query(models.SaleItem).filter(models.SaleItem.id == item.item_id).first()
        price_per_item = sale_item.price
        total_price = price_per_item * item.quantity
    
        cash = models.Cash(label="sale_", amount=total_price, label_id = "sale_" + str(new_item.id), creator=current_user.id)
        db.add(cash)
        db.commit()
        db.refresh(cash)

    return {"message": "created"}

