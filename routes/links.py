from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import Optional


router = APIRouter(prefix="/links", tags=['Links'])

@router.get('/')
def get_links(db: Session = Depends(get_db), current_user : schemas.User =Depends(oauth2.get_current_user)):
    role = current_user.role.value
    if role == "no_role":
        links = []
        paths = []
        return {"links": links, "paths": paths}
    elif role == "retailer":
        links = ["Products", "Sales"]
        paths = ["/products", "/products/sales"]
        return {"links": links, "paths": paths}
    elif role == "kitchen":
        links = ["Kitchen Products", "Material Requests", "Stock Items", "Products"]
        paths = ["/kitchen/products", "/kitchen/requests", "/stock/items", "products"]
        return {"links": links, "paths": paths}
    elif role == "boss" or role == "deputy_boss":
        paths = ["/kitchen/products", "/kitchen/requests", "/products", "/products/sales", "/stock", "/stock/items", "/stock/purchases", "/cash", "/users"];
        links = ["Kitchen Products", "Material Requests", "Products", "Sales", "Stock", "Stock Items", "Purchases", "Cash", "Users"]
        return {"links": links, "paths": paths}
    else:
        paths = ["/kitchen/products", "/kitchen/requests", "/products", "/products/sales", "/stock", "/stock/items", "/stock/purchases"];
        links = ["Kitchen Products", "Material Requests", "Products", "Sales", "Stock", "Stock Items", "Purchases"]
        return {"links": links, "paths": paths}