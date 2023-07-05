# app/service/user_service.py

from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from datetime import datetime, timedelta

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not user.hashed_password or not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.hashed_password)
    next_billing_date = datetime.now() + timedelta(days=30)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        credit_limit=user.credit_limit,
        next_billing_date=next_billing_date
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: UserUpdate):
    db_user = get_user_by_username(db, username=user.username)
    if not db_user:
        return None
    if not verify_password(user.old_password, db_user.hashed_password):
        return None
    db_user.hashed_password = get_password_hash(user.new_password)
    db.commit()
    db.refresh(db_user)
    return db_user
