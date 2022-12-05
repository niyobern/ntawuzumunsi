import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class Roles(enum.Enum):
    boss = 'boss'
    deputy_boss = "deputy_boss"
    manager = 'manager'
    store_keeper = "store_keeper"
    retailer = "retailer"
    kitchen = "kitchen"
    eservices = 'e-services'
    cashier = 'cashier'
    no_role = "no_role"

class StockItem(Base):
    __tablename__ =  "stock_items"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    creator = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    description = Column(String)
    requisitions = relationship("Requisition")
    material_request = relationship("MaterialRequest")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False, unique=True)
    role = Column(Enum(Roles), nullable=False, server_default="no_role")
    password = Column(String, nullable=False)
    stock_items = relationship("StockItem")
    requisitions = relationship("Requisition")
    sale_items = relationship("SaleItem")
    sales = relationship("Sale")
    material_requests = relationship("MaterialRequest")
    kitchen_products = relationship("KitchenProduct")
    e_services = relationship("Eservice")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Requisition(Base):
    __tablename__ = "requisitions"
    id = Column(Integer, primary_key=True, nullable=False)
    stock_id = Column(Integer, ForeignKey("stock_items.id", ondelete="CASCADE"))
    quantity = Column(Float, nullable=False)
    creator = Column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    tag = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sale = relationship("Sale")
    kitchen_product = relationship("KitchenProduct")
    creator = Column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, nullable=False)
    item_id = Column(ForeignKey("sale_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    creator = Column(ForeignKey("users.id", ondelete="CASCADE"))
    tag = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Eservice(Base):
    __tablename__ = "e_services"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    tag = Column(String)
    price = Column(Float, nullable=False)
    creator = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class KitchenProduct(Base):
    __tablename__ = "kitchen_products"
    id = Column(Integer, primary_key=True, nullable=False)
    item_id = Column(ForeignKey("sale_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    creator = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class MaterialRequest(Base):
    __tablename__ = "material_requests"
    id = Column(Integer, primary_key=True, nullable=False)
    stock_id = Column(ForeignKey("stock_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    creator = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String)
    accepted = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

