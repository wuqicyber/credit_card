from sqlalchemy import union_all
from sqlalchemy.orm import Session
from app.models import Payment, Repayment
from sqlalchemy import literal
from app.database import get_redis
from typing import List
import json

from datetime import datetime

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    else:
        return x


def row2dict(row):
    return {col: datetime_handler(getattr(row, col)) for col in row._fields}


def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 10):

    payments = db.query(literal('payment').label('type'), Payment.id.label('id'), Payment.principal.label('amount'), Payment.timestamp.label('timestamp')).filter(Payment.user_id == user_id)
    repayments = db.query(literal('repayment').label('type'), Repayment.id.label('id'), Repayment.repayment_amount.label('amount'), Repayment.repayment_date.label('timestamp')).filter(Repayment.user_id == user_id)

    transactions = union_all(payments, repayments).alias()
    results = db.query(transactions).order_by(transactions.c.timestamp.desc()).offset(skip).limit(limit).all()
    results = [row2dict(row) for row in results]
    return results

def cache_transactions(redis_db, transactions: List[dict], key, expire_time=60 * 60):
    serialized_transactions = json.dumps(transactions)
    redis_db.set(key, serialized_transactions, ex=expire_time)

def clear_cache(redis_db:get_redis(), user_id):
    """Clear all transaction cache for a user."""
    user_key_pattern = f'user:{user_id}:*'
    for key in redis_db.scan_iter(match=user_key_pattern):
        redis_db.delete(key)


#




