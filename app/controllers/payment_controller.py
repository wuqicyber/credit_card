# app/controller/payment_controller.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PaymentCreate, Payment, User
from app.services import payment_service, cache_service
from app.auth import get_current_user
from app.database import get_redis
from fastapi import Depends
from redis import Redis
router = APIRouter()

@router.post("/create", response_model=Payment)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), redis_db: Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    db_payment = payment_service.create_payment(db, payment=payment)
    if db_payment is None:
        raise HTTPException(status_code=400, detail="Error creating payment")

    cache_service.delete_from_cache(redis_db, payment.user_id, "payments")
    cache_service.delete_from_cache(redis_db, payment.user_id, "transactions")
    return db_payment

@router.get("/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_payment = payment_service.get_payment_by_id(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@router.get("/user/{user_id}")
def get_payments(user_id: int, skip: int = 0, limit: int = 10,db: Session = Depends(get_db), redis_db: Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    key =  f'user:{user_id}:payments:{skip}:{limit}'
    cached_payments = cache_service.get_from_cache(redis_db, key)
    if cached_payments is not None:
        return cached_payments
    db_payments = payment_service.get_payments_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    if db_payments is None:
        raise HTTPException(status_code=404, detail="Payments not found")
    cache_service.set_to_cache(redis_db, key, db_payments)
    return db_payments


