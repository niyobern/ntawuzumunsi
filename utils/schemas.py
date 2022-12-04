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
    name: str
    email: EmailStr
    phone: str
    role: Role | None = None

class UserCreate(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str | None = None

class StockItem(BaseModel):
    id : str | None
    name: str
    unit : str
    price: float
    description: str