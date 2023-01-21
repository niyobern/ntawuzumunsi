from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import models
from alembic import command
from database.database import engine
from utils.schemas import User
from routes import user, auth, stock_item, purchase, sale_item, sale, kitchen_product, material_request, eservice, cash, links, summary, stock, stockdeprecations, commande
from routes.reports import cashes, kitchen, material_requests, purchases, sales, stockdeprecation

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

origins = ["https://www.lavajavahouse.net", "https://lavajavahouse.net", "*", "http://localhost:3000", "https://main.d2yic9lxsfg9sy.amplifyapp.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "content-type", "Access-Control-Allow-Origin",  "*",],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(stock_item.router)
app.include_router(purchase.router)
app.include_router(sale_item.router)
app.include_router(sale.router)
app.include_router(kitchen_product.router)
app.include_router(material_request.router)
app.include_router(eservice.router)
app.include_router(cashes.router)
app.include_router(stock.router)
app.include_router(links.router)
app.include_router(summary.router)
app.include_router(stockdeprecations.router)
app.include_router(cash.router)
app.include_router(kitchen.router)
app.include_router(material_requests.router)
app.include_router(purchases.router)
app.include_router(sales.router)
app.include_router(stockdeprecation.router)
app.include_router(commande.router)


@app.get('/')
def index():
    return {"message": "from AWS"}
