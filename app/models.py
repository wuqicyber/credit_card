from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    is_paid = Column(Boolean, default=False)  # 新增字段，表示是否已还款
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

