import unittest
from unittest.mock import Mock, patch
from app.services import user_service
from app.models import User
from app.schemas import UserCreate, UserUpdate
from unittest.mock import patch, MagicMock

class UserServiceTestCase(unittest.TestCase):
    @patch('app.services.user_service.get_user_by_username')
    @patch('app.services.user_service.get_password_hash')
    def test_create_user(self, mock_get_password_hash, mock_get_user_by_username):
        # Mock the return value of get_user_by_username
        mock_get_user_by_username.return_value = None

        # Mock the return value of get_password_hash
        mock_get_password_hash.return_value = 'hashed_password'

        # Mock the database session
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Test user creation
        user_create = UserCreate(username='test_username', hashed_password='test_password', credit_limit=1000)
        result = user_service.create_user(mock_db, user_create)
        self.assertEqual(result.username, 'test_username')
        self.assertEqual(result.hashed_password, 'hashed_password')
        self.assertEqual(result.credit_limit, 1000)
        self.assertTrue(mock_db.add.called)
        self.assertTrue(mock_db.commit.called)
        self.assertTrue(mock_db.refresh.called)



    @patch('app.services.user_service.get_user_by_username')
    def test_authenticate_user(self, mock_get_user_by_username):
        # Mock the return value of get_user_by_username
        mock_user = Mock(spec=User)
        mock_user.hashed_password = 'hashed_password'

        # Mock the database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_get_user_by_username.return_value = mock_user

        # Test successful authentication
        with patch('app.services.user_service.verify_password', return_value=True):
            result = user_service.authenticate_user(mock_db, 'test_username', 'test_password')
            self.assertEqual(result.hashed_password, mock_user.hashed_password)

        # Test failed authentication (wrong password)
        with patch('app.services.user_service.verify_password', return_value=False):
            result = user_service.authenticate_user(mock_db, 'test_username', 'wrong_password')
            self.assertFalse(result)

        # Test failed authentication (user not found)
        # Test failed authentication (user not found)
        mock_user.hashed_password = None
        mock_get_user_by_username.return_value = mock_user
        result = user_service.authenticate_user(mock_db, 'non_existent_username', 'test_password')
        self.assertFalse(result)

    @patch('app.services.user_service.get_user_by_username')
    def test_update_user_password(self, mock_get_user_by_username):
        # Mock the return value of get_user_by_username
        mock_user = Mock(spec=User)
        mock_user.hashed_password = 'old_hashed_password'
        mock_get_user_by_username.return_value = mock_user

        # Mock the database session
        mock_db = Mock()

        # Test successful password update
        with patch('app.services.user_service.verify_password', return_value=True):
            with patch('app.services.user_service.get_password_hash', return_value='new_hashed_password'):
                user_update = UserUpdate(username='test_username', old_password='old_password', new_password='new_password')
                result = user_service.update_user_password(mock_db, user_update)
                self.assertEqual(result.hashed_password, 'new_hashed_password')

        # Test failed password update (wrong old password)
        with patch('app.services.user_service.verify_password', return_value=False):
            user_update = UserUpdate(username='test_username', old_password='wrong_old_password', new_password='new_password')
            result = user_service.update_user_password(mock_db, user_update)
            self.assertIsNone(result)

        # Test failed password update (user not found)
        mock_get_user_by_username.return_value = None
        user_update = UserUpdate(username='non_existent_username', old_password='old_password', new_password='new_password')
        result = user_service.update_user_password(mock_db, user_update)
        self.assertIsNone(result)

    # Add test cases for other functions in user_service in a similar way...

if __name__ == '__main__':
    unittest.main()
