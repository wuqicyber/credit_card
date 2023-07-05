# app/controllers/user_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.services import user_service
from app.schemas import UserCreate, UserUpdate, User, UserInfo
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from datetime import timedelta
from sqlalchemy.orm import Session
from app.auth import create_access_token, get_current_user

ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter()

@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_service.create_user(db=db, user=user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/info/{user_id}", response_model=UserInfo)
def get_info(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = user_service.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/update_password")
def update_password(user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = user_service.update_user_password(db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Incorrect old password or username not found")
    return {"msg": "Password updated successfully"}
