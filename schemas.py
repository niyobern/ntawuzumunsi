from typing import List
from pydantic import BaseModel, EmailStr
from enum import Enum

class Roles(Enum):
    boss = 'boss'
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
    role: Roles | None = None