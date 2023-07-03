from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PaymentBase(BaseModel):
    principal: float
    timestamp: Optional[datetime]
    repayment_due_date: datetime
    is_overdue: bool

class PaymentCreate(PaymentBase):
    user_id: int

class Payment(PaymentBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class RepaymentBase(BaseModel):
    repayment_amount: float
    repayment_date: Optional[datetime]

class RepaymentCreate(RepaymentBase):
    user_id: int
    payment_id: int

class Repayment(RepaymentBase):
    id: int
    user_id: int
    payment_id: int

    class Config:
        orm_mode = True

# app/schemas.py
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    hashed_password: str
    credit_limit: Optional[float] = 1000.0
    # next_billing_date: Optional[datetime]
# next_billing_date不应该由用户提供，而是自动创建成创建时间之后的一个月
class UserUpdate(UserBase):
    old_password: str
    new_password: str

class User(UserBase):
    id: int
    credit_limit: float
    next_billing_date: datetime

    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    username: str
    credit_limit: float
    next_billing_date: datetime

    class Config:
        orm_mode = True

