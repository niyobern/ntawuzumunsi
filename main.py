from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import models
from database.database import engine
from utils.schemas import User
from routes import user, auth, stock_item, purchase, sale_item, sale, kitchen_product, material_request, eservice, cash, links

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

origins = ["https://lavajava-ltl3.vercel.app/", "https://.*\.vercel", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["Authorization", "content-type","*"],
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
app.include_router(cash.router)
app.include_router(links.router)

@app.get('/')
def index():
    return {"message": "Hello from AWS"}
