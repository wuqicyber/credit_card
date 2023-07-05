from unittest.mock import MagicMock, patch
from collections import namedtuple
import unittest
from app.services.transaction_service import get_transactions

class TransactionServiceTest(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.user_id = 1
        self.skip = 0
        self.limit = 10

    @patch("app.services.transaction_service.union_all")
    def test_get_transactions(self, mock_union_all):
        # 创建一个mock查询对象
        mock_query = MagicMock()

        # 配置mock查询对象的方法返回自身，以支持链式调用
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query

        # 创建一个namedtuple类型，模拟SQLAlchemy的Row对象
        MockRow = namedtuple("Row", ["id", "type", "amount", "timestamp"])

        # 配置mock查询对象的all方法返回一个测试用的数据
        mock_query.all.return_value = [MockRow(1, "payment", 100.0, "2023-07-01")]

        # 配置mock的union_all函数返回mock查询对象
        mock_union_all.return_value = mock_query

        # 配置数据库的query方法返回mock查询对象
        self.db.query.return_value = mock_query

        # 调用被测试的函数
        transactions = get_transactions(self.db, self.user_id, self.skip, self.limit)

        # 断言函数返回的数据与预期相符
        self.assertEqual(transactions, [{"id": 1, "type": "payment", "amount": 100.0, "timestamp": "2023-07-01"}])
