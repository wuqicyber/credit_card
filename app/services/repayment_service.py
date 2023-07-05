# app/services/repayment_service.py
from datetime import datetime
from datetime import datetime, timedelta
from app.models import Payment, User, Repayment
from app.schemas import PaymentBase
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

def get_due_payments(db: Session, user_id: int):
    today = datetime.today()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    return db.query(Payment).filter(
        Payment.user_id == user_id,
        Payment.is_paid == False,
        or_(
            Payment.is_overdue == True,
            and_(
                (Payment.repayment_due_date).__le__(today+timedelta(days=10)), # 这里调试了好久，repayment_due_date + timedelta不能成功比较，把time_delta加在today后面就可以成功表
                Payment.repayment_due_date.__ge__(today)
            )
        )
    ).all()
# 问gpt，Payment.repayment_due_date 是一个 SQLAlchemy Column，其类型是 DateTime，而 timedelta(days=-10) 是一个 Python timedelta 对象。虽然在 Python 中，你可以直接把 datetime 对象和 timedelta 对象相加，但在 SQLAlchemy 查询中，这样的操作可能会导致错误。


def calculate_due_amount(payment: Payment):
    if payment.is_overdue:
        overdue_days = (datetime.today() - payment.repayment_due_date).days
        # Assuming r is 0.003
        loan_days = (datetime.today() - payment.timestamp).days
        interest = loan_days * 0.003 * payment.principal
        penalty = overdue_days * 0.003 * payment.principal
        return payment.principal + interest + penalty
    else:
        return payment.principal



def make_repayment(db: Session, user_id: int, payment_id: int):
    today = datetime.today()
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    if not payment or not user:
        return {"error": "User or Payment not found"}

    if payment.is_paid:
        return {"message": "You have already paid, no repayment needed"}

    if payment.is_overdue or today >= payment.repayment_due_date - timedelta(days=10):
        due_amount = calculate_due_amount(payment)
        payment.is_paid = 1
        user.credit_limit += payment.principal  # update credit_limit

        repayment = Repayment(
            user_id=user_id,
            payment_id=payment_id,
            repayment_amount=due_amount,
            repayment_date=today
        )
        db.add(repayment)
        db.commit()
        return {"message": f"You have paid {due_amount}, and your credit limit is now {user.credit_limit}"}

    return {"message": "It's not billing date yet, no repayment needed"}


# 函数需要实现的功能为：输入user_id, payment_id，首先查询该账单是否需要还款，先检查该账单是否是is_paid.如果已经付费，那么
# 返回你已经付费了，不需要还款。再去检查账单是否overdue，如果overdue了，那么返回你已经支付了<计算需要还款的金额>,将is_paid设置为
# 1，如果没有overdue，再去看一下当前是否在最后还款日的前十天内，如果在，那么返回你已经支付了<计算需要还款的金额>,将is_paid设置为1
# 如果不是，返回，还未到出账日，你当前不需要还款。 同时，记得更新credit_limit
# 还要把repayment record加入repayments这张table


def get_repayment_records(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    repayments = db.query(Repayment).filter(Repayment.user_id == user_id).offset(skip).limit(limit).all()
    return repayments
