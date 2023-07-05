import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta
from app.services.payment_service import create_payment
from app.schemas import PaymentCreate
from app.models import Payment, User


class PaymentServiceTest(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.user_id = 1
        self.principal = 1000
        self.payment_create = PaymentCreate(user_id=self.user_id, principal=self.principal)
        self.user = User(id=self.user_id, credit_limit=2000, next_billing_date=datetime.now())
        self.db.query().filter().first.return_value = self.user

    def test_create_payment(self):
        # Test case when credit_limit is more than principal amount
        payment = create_payment(self.db, self.payment_create)
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.user_id, self.user_id)
        self.assertEqual(payment.principal, self.principal)
        self.assertEqual(self.user.credit_limit, 1000)

    def test_create_payment_credit_limit_exceeded(self):
        # Test case when credit_limit is less than principal amount
        self.user.credit_limit = 500
        self.assertRaises(ValueError, create_payment, self.db, self.payment_create)


if __name__ == "__main__":
    unittest.main()
