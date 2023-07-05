from app.services import transaction_service
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.auth import get_current_user
from app.schemas import User
import redis
import json
from app.database import get_redis

router = APIRouter()
@router.get("/transactions/{user_id}")
def get_transactions(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), redis_db: redis.Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    redis_key = f'user:{user_id}:transactions:{skip}:{limit}'
    cached_transactions = redis_db.get(redis_key)
    if cached_transactions:
        # Decode transactions from JSON
        return json.loads(cached_transactions)
    transactions = transaction_service.get_transactions(db, user_id, skip, limit)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    transaction_service.cache_transactions(redis_db, transactions, redis_key)
    return {"transactions": transactions}








