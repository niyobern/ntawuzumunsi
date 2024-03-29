from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import models
from utils import schemas, utils, oauth2
from database.database import get_db
from typing import List

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
    role = "no_role"
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
    
@router.get('/')
def return_get_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    users = db.query(models.User).all()
    users_info = []
    for user in users:
        info = {"Name": user.name, "email": user.email, "phone": user.phone, "role": user.role.value, "id": user.id}
        users_info.append(info)
    return users_info


@router.patch('/')
def update_user(users: List[schemas.UserUpdate], db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role.value not in ("boss", "deputy_boss"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are unauthorised to do so") 
    for user in users:
        user_role = user.role.value
        user.role = user_role
        user_query = db.query(models.User).filter(models.User.id == user.id)
        found_query = user_query.first()
        if found_query == None:
            raise HTTPException(status_code=status.HTTTP_403_FORBIDDEN, detail="Not Found")
        user_query.update(user.dict(), synchronize_session=False)
        db.commit()
    return {"message": "Updated"}

@router.patch("/password")
def change_password(password_change: schemas.PasswordChange, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if not utils.verify(password_change.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Password")
    new_password = utils.hash(password_change.password)
    fetch = db.query(models.User).filter(models.User.id == current_user.id)
    fetch.update({"password": new_password})
    db.commit()
    return {"message": 'Succesfully Changed'}


@router.get('/{id}')
def get_user(id: int, db: Session = Depends(get_db), user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user

