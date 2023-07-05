# repayment_test.py
import unittest
from unittest.mock import Mock, patch
from app.services.repayment_service import get_due_payments, calculate_due_amount, make_repayment, get_repayment_records
from app.models import Payment, User, Repayment
from datetime import datetime, timedelta

class RepaymentServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.user_id = 1
        self.payment_id = 1
        self.payment = Payment(id=self.payment_id, user_id=self.user_id, is_paid=False, is_overdue=False,
                               repayment_due_date=datetime.today() + timedelta(days=5),
                               timestamp=datetime.today() - timedelta(days=10), principal=1000)
        self.user = Mock()
        self.user.id = self.user_id
        self.user.credit_limit = 2000  # add credit_limit to mock user
        self.db.query().filter().first.side_effect = [self.payment,
                                                      self.user]  # return different results for subsequent calls

    @patch("app.services.repayment_service.datetime")
    def test_get_due_payments(self, mock_datetime):
        mock_datetime.today.return_value = datetime.today()
        self.db.query().filter().all.return_value = [self.payment]
        payments = get_due_payments(self.db, self.user_id)
        self.assertEqual(payments, [self.payment])

    def test_calculate_due_amount(self):
        due_amount = calculate_due_amount(self.payment)
        self.assertEqual(due_amount, 1000)

    @patch("app.services.repayment_service.datetime")
    def test_make_repayment(self, mock_datetime):
        mock_datetime.today.return_value = datetime.today() + timedelta(days=5)
        response = make_repayment(self.db, self.user_id, self.payment_id)
        self.assertEqual(response, {"message": f"You have paid {1000}, and your credit limit is now {3000}"})

    def test_get_repayment_records(self):
        repayments = [Repayment(user_id=self.user_id, payment_id=self.payment_id, repayment_amount=1000, repayment_date=datetime.today())]
        self.db.query().filter().offset().limit().all.return_value = repayments
        results = get_repayment_records(self.db, self.user_id)
        self.assertEqual(results, repayments)

if __name__ == "__main__":
    unittest.main()

