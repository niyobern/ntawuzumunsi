from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
import datetime

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# /users/
# /users


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password - user.password
    # user_dict = user.dict()
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    role = "boss"
    user_dict = user.dict()
    user_dict["role"] = role
    new_user = models.User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@router.get('/current')
def return_user(db: Session = Depends(get_db), user: schemas.User = Depends(oauth2.get_current_user)):
    return user

@router.patch('/{id}')
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are unauthorised to do so") 
    user_role = user.role.value
    user.role = user_role
    user_query = db.query(models.User).filter(models.User.id == id)
    found_query = user_query.first()
    if found_query == None:
        raise HTTPException(status_code=status.HTTTP_403_FORBIDDEN, detail="Not Found")
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()
    return user



@router.get('/{id}')
def get_user(id: int, db: Session = Depends(get_db), user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user

