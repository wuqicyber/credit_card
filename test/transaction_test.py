import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.transaction_service import TransactionService
from app.models import Transaction, User, TransactionType, InterestAndPenalty

class TestTransactionService(unittest.TestCase):

    @patch('app.services.transaction_service.datetime')
    def test_create_transaction_payment_exceeds_limit(self, mock_datetime):
        mock_db = Mock()
        mock_redis_db = Mock()
        mock_user = Mock(spec=User)
        mock_user.balance = 1000
        mock_user.credit_limit = 2000
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        transaction_service = TransactionService(mock_db, mock_redis_db)

        with self.assertRaises(Exception):
            transaction_service.create_transaction(1, 5000, TransactionType.payment)

        mock_db.query.assert_called_once_with(User)

    @patch('app.services.transaction_service.datetime')
    def test_create_transaction_success(self, mock_datetime):
        mock_db = Mock()
        mock_redis_db = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.balance = 5000
        mock_user.credit_limit = 2000
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_datetime.now.return_value = datetime(2023, 7, 3)

        transaction_service = TransactionService(mock_db, mock_redis_db)
        transaction = transaction_service.create_transaction(1, 1000, TransactionType.payment)

        self.assertEqual(transaction.user_id, 1)
        self.assertEqual(transaction.amount, 1000)
        self.assertEqual(transaction.transaction_category, TransactionType.payment)
        self.assertEqual(transaction.due_date, datetime(2023, 7, 3) + timedelta(days=30))
        self.assertEqual(transaction.repayment_status, False)
        self.assertEqual(transaction.remained_unpaid_amount, 1000 + (1000 * 0.003))

        mock_db.query.assert_called_once_with(User)

    def test_get_transactions(self):
        mock_db = Mock()
        mock_redis_db = Mock()
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            Mock(spec=Transaction), Mock(spec=Transaction)]

        transaction_service = TransactionService(mock_db, mock_redis_db)
        transactions = transaction_service.get_transactions(1, 10, 0)

        self.assertEqual(len(transactions), 2)
        mock_db.query.assert_called_once_with(Transaction)

if __name__ == '__main__':
    unittest.main()
