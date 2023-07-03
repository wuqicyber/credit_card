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

Create Time: 2023/7/3

"""

import pytest
from app.services.user_service import UserService
from app.models import User
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from app.schemas import UserCreate


@patch("app.services.user_service.get_password_hash")
def test_create_user(mock_get_password_hash):
    mock_session = MagicMock(spec=Session)
    mock_get_password_hash.return_value = "hashed_password"
    user_service = UserService(mock_session, None)

    user_create = UserCreate(username="test", password="test", credit_limit=1000)

    user_service.create_user(user_create)

    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()

    added_user: User = mock_session.add.call_args[0][0]
    assert added_user.username == "test"
    assert added_user.hashed_password == "hashed_password"
    assert added_user.credit_limit == 1000


@patch("app.services.user_service.verify_password")
def test_authenticate_user(mock_verify_password):
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_session.query().filter().first.return_value = mock_user

    user_service = UserService(mock_session, None)

    mock_verify_password.return_value = True

    assert user_service.authenticate_user(mock_session, "test", "test") is mock_user

    mock_verify_password.return_value = False

    assert not user_service.authenticate_user(mock_session, "test", "test")

    mock_session.query().filter().first.return_value = None

    assert not user_service.authenticate_user(mock_session, "test", "test")


def test_get_balance_and_credit_limit():
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_session.query().filter().first.return_value = mock_user

    user_service = UserService(mock_session, None)

    assert user_service.get_balance_and_credit_limit(1) == (mock_user.balance, mock_user.credit_limit)

    mock_session.query().filter().first.return_value = None

    assert user_service.get_balance_and_credit_limit(1) is None


@patch("app.services.user_service.get_password_hash")
def test_update_password(mock_get_password_hash):
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_session.query().filter().first.return_value = mock_user
    mock_get_password_hash.return_value = "hashed_password"

    user_service = UserService(mock_session, None)

    assert user_service.update_password(1, "new_password") is mock_user
    assert mock_user.hashed_password == "hashed_password"

    mock_session.query().filter().first.return_value = None

    assert user_service.update_password(1, "new_password") is None




