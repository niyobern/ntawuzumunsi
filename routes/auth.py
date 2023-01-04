from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from utils import schemas
from sqlalchemy import or_

from database import database, models
from utils import  utils, oauth2, schemas

router = APIRouter(tags=['Authentication'])


@router.post('/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(or_(models.User.email == user_credentials.username, models.User.phone == user_credentials.username)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Username")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Password")

    # create a token
    # return token

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    if user.email == "berniyo@outlook.com":
        return {"access_token": access_token, "token_type": "Bearer"}

    return f"Bearer {access_token}"