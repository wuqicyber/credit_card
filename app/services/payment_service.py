# app/services/payment_service.py

from sqlalchemy.orm import Session
from app.models import Payment
from app.schemas import PaymentCreate
from app.services import user_service, cache_service
from datetime import timedelta, datetime
from fastapi import HTTPException



def create_payment(db: Session, payment: PaymentCreate):
    # Query for the user to get the next_billing_date
    user = user_service.get_user_by_id(db, user_id=payment.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Decrease the credit_limit of the user
    if user.credit_limit < payment.principal:
        raise HTTPException(status_code=404, detail="Credit limit exceeded")
    user.credit_limit -= payment.principal

    repayment_due_date = user.next_billing_date + timedelta(days=10)

    db_payment = Payment(
        user_id=payment.user_id,
        principal=payment.principal,
        timestamp=datetime.now(),
        repayment_due_date=repayment_due_date,
        is_overdue=False,
        is_paid=False
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


# repayment due date 应该等于next_billing_date再加上十天。
def get_payment_by_id(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_payments_by_user_id(db: Session, user_id: int , skip: int = 0, limit: int = 10):
    payments = db.query(Payment).filter(Payment.user_id == user_id).offset(skip).limit(limit).all()
    return payments