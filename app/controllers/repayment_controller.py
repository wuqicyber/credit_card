# app/controller/repayment_controller.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment
from app.schemas import User
from app.services import repayment_service, cache_service
from app.auth import get_current_user
from app.database import get_redis
from fastapi import Depends
from redis import Redis

router = APIRouter()

@router.get("/due_payments/{user_id}")
def get_due_payments(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payments = repayment_service.get_due_payments(db, user_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No due payments found")

    payment_details = []
    total_due_amount = 0

    for payment in payments:
        due_amount = repayment_service.calculate_due_amount(payment)
        total_due_amount += due_amount
        payment_info = {"payment": payment, "due_amount": due_amount}
        payment_details.append(payment_info)

    return {"payments": payment_details, "total_due_amount": total_due_amount}

@router.get("/due_amount/{payment_id}")
def calculate_due_amount(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    due_amount = repayment_service.calculate_due_amount(payment)
    return {"due_amount": due_amount}

@router.post("/make_repayment/{user_id}/{payment_id}")
def make_repayment(user_id: int, payment_id: int, db: Session = Depends(get_db), redis_db: Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    result = repayment_service.make_repayment(db, user_id, payment_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    cache_service.delete_from_cache(redis_db, user_id, "repayments")
    cache_service.delete_from_cache(redis_db, user_id, "transactions")
    return result

@router.get("/repayments/{user_id}")
def get_repayments(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), redis_db: Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    key = f'user:{user_id}:repayments:{skip}:{limit}'
    cached_repayments = cache_service.get_from_cache(redis_db, key)
    if cached_repayments is not None:
        return cached_repayments
    repayments = repayment_service.get_repayment_records(db, user_id, skip, limit)
    if not repayments:
        raise HTTPException(status_code=404, detail="No repayments found")
    cache_service.set_to_cache(redis_db, key, cached_repayments)
    return {"repayments": repayments}



