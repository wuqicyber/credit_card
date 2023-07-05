"""

   ┏┓   ┏┓ + +
  ┏┛┻━━━┛┻┓ + +
  ┃   ━   ┃ ++ + + +
  ┃ ████━████  ┃+
  ┃       ┃ +
  ┃   ┻   ┃ + +
  ┗━┓   ┏━┛
    ┃   ┃ + + + +
    ┃   ┃ +   神兽保佑,代码无bug
    ┃   ┃ +
    ┃   ┗━━━┓ + +
    ┃       ┣┓
    ┃       ┏┛
    ┗┓┓┏━┳┓┏┛ + + + +
     ┃┫┫ ┃┫┫
     ┗┻┛ ┗┻┛+ + + +

Create Time: 2023/7/4

"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import User, Payment
from sqlalchemy import and_

def update_billing_and_overdue():
    # Get a session
    db = SessionLocal()

    expired_users = db.query(User).filter(User.next_billing_date < datetime.today()).all()
    for user in expired_users:
        user.next_billing_date += timedelta(days=30)

    # Check overdue payments
    overdue_payments = db.query(Payment).filter(
        and_(
            Payment.is_paid == False,
            Payment.repayment_due_date < datetime.today()
        )
    ).all()

    for payment in overdue_payments:
        payment.is_overdue = True

    db.commit()
    db.close()

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_billing_and_overdue, 'interval', minutes=1)
scheduler.start()
