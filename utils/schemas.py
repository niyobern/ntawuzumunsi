from typing import List
from pydantic import BaseModel, EmailStr
from enum import Enum
class Role(Enum):
    boss = "boss"
    deputy_boss = "deputy_boss"
    manager = 'manager'
    store_keeper = "store_keeper"
    retailer = "retailer"
    kitchen = "kitchen"
    e_services = 'e_services'
    cashier = 'cashier'
    no_role = "no_role"

class User(BaseModel):
    id: int | None = None
    name: str
    email: EmailStr
    phone: str
    role: Role | None = None
    class Config:
        orm_mode = True


class UserCreate(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str | None = None

class StockItem(BaseModel):
    name: str
    unit : str
    price: float
    description: str


class Requisition(BaseModel):
    stock_id: int
    quantity: float
    tag: str

class SaleItem(BaseModel):
    name: str
    unit: str
    price: float
    description: str

class Sale(BaseModel):
    item_id: int
    quantiy: float
    tag: str

class KitchenProduct(BaseModel):
    item_id: int
    quantity: float
    decription: str

class MaterialRequest(BaseModel):
    stock_id: int
    quantity: float
    tag: str
    accepted: bool | None = None