from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional
from typing import List

router = APIRouter(prefix="/sales", tags=['Sales'])

@router.get('/')
def get_sales(db: Session = Depends(get_db), current_user : schemas.User =Depends(oauth2.get_current_user),
  limit: int = 100, skip: int = 0, search: Optional[str] = "", start: str = "2022-12-18", end: str = "2023-12-18"):
    if current_user.role.value not in ("manager", "boss", "deputy_boss", "retailer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed to view this")
    sales = db.query(models.Sale).filter(models.Sale.created_at.between(start, end)).filter(models.Sale.tag.contains(search)).order_by(models.Sale.created_at.desc()).limit(limit).offset(skip).all()
    sales_info = []
    for sale in sales:
        time = str(sale.created_at)
        sale_item = db.query(models.SaleItem).filter(models.StockItem.id == sale.item_id).first()
        info = {"Id": sale.id, "Product_id": sale_item.name, "Quantity": sale.quantity, "Creator": sale.creator, "date": time[:10], "tag": sale.tag}
        sales_info.append(info)
    return sales_info


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
    
        cash = models.Cash(label="sale", amount=total_price, label_id = "sale_" + str(new_item.id), creator=current_user.id)
        db.add(cash)
        db.commit()
        db.refresh(cash)

    return {"message": "created"}

