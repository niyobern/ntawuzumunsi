from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
from datetime import datetime  
from datetime import timedelta  
from typing import List

router = APIRouter(prefix="/summary", tags=['Summary'])

end = datetime.utcnow()
start = end - timedelta(days=30)

@router.get('/')
def get_summary(db: Session = Depends(get_db), current_user : schemas.User = Depends(oauth2.get_current_user), start: str = start, end: str = end):
    results = []
    if current_user.role.value in ("manager", "boss", "deputy_boss", "retailer"):
        sales = db.query(models.Sale, models.SaleItem).filter(models.Sale.item_id == models.SaleItem.id).filter(models.KitchenProduct.created_at.between(start, end)).all()
        purchases_values = [x.price for x in sales]
        value = sum(purchases_values)
        sales_count = len(sales)
        results.append({"title": "Sales", "value1": f"{sales_count} Sales valued {value}", "value2": {"from": start, "end": end}})
    if current_user.role.value in ("manager", "boss", "deputy_boss", "store_keeper"):
        purchases = db.query(models.Requisition, models.StockItem).filter(models.StockItem.id == models.Requisition.stock_id).filter(models.Requisition.created_at.between(start, end)).all()
        purchases_count = len(purchases)
        values = [x.price for x in purchases]
        value = sum(values)
        results.append({"title": "Purchases", "value1": f"{purchases_count} Sales valued {value}", "value2": {"from": start, "end": end}})
    if current_user.role.value in ("manager", "boss", "deputy_boss", "store_keeper"):
        purchases = db.query(models.MaterialRequest, models.StockItem).filter(models.StockItem.id == models.MaterialRequest.stock_id).filter(models.MaterialRequest.created_at.between(start, end)).all()
        purchases_count = len(purchases)
        values = [x.price for x in purchases]
        value = sum(values)
        results.append({"title": "Items Requested From Stock", "value1": f"{purchases_count} with {value} value", "value2": {"from": start, "end": end}})
    if current_user.role.value in ("manager", "boss", "deputy_boss", "store_keeper"):
        purchases = db.query(models.MaterialRequest, models.StockItem).filter(models.StockItem.id == models.MaterialRequest.stock_id).filter(models.MaterialRequest.created_at.between(start, end)).filter(models.MaterialRequest.accepted == True).all()
        purchases_count = len(purchases)
        values = [x.price for x in purchases]
        value = sum(values)
        results.append({"title": "Items Gone out of Stock", "value1": f"{purchases_count} with {value} value", "value2": {"from": start, "end": end}})
    if current_user.role.value in ("manager", "boss", "deputy_boss"):
        purchases = db.query(models.Cash).filter(models.Cash.amount > 0 ).filter(models.Cash.created_at.between(start, end)).all()
        purchases_count = len(purchases)
        values = [x.amount for x in purchases]
        value = sum(values)
        results.append({"title": "Transactions Returned Money", "value1": f"{purchases_count} with {value} total value", "value2": {"from": start, "end": end}})
    if current_user.role.value in ("manager", "boss", "deputy_boss"):
        purchases = db.query(models.Cash).filter(models.Cash.amount < 0 ).filter(models.Cash.created_at.between(start, end)).all()
        purchases_count = len(purchases)
        values = [x.amount for x in purchases]
        value = sum(values)
        results.append({"title": "Transactions Costed Money", "value1": f"{purchases_count} with {value} total value", "value2": {"from": start, "end": end}})
    return results


