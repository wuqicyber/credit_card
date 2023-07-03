from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(200), nullable=False)
    credit_limit = Column(Float, default=1000.0)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    payments = relationship("Payment", back_populates="user")
    repayments = relationship("Repayment", back_populates="user")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    principal = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    repayment_due_date = Column(DateTime(timezone=True))
    is_overdue = Column(Boolean, default=False)
    user = relationship("User", back_populates="payments")

class Repayment(Base):
    __tablename__ = "repayments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    repayment_amount = Column(Float)
    repayment_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="repayments")
    payment = relationship("Payment")


# 好的，下面我的app.service文件夹中分别创建了user_service.py,payment_service.py,repayment_service.py等三个文件，
# 我在app.controller文件夹中分别创建了user_controller.py, payment_controller.py, repayment_controller.py
# 我的core文件夹中有个名为security.py中有如下代码
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# 请先帮我完成user_service.py 与 user_controller.py