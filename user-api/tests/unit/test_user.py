import pytest
from unittest.mock import patch

from loguru import logger

from ..unit import UserMock
from user_api.business.user import insert_user, update_user
from user_api.exceptions.user import UserAlreadyInserted


@patch("user_api.business.user.insert_user")
def test_insert_user_success(mock_insert_user):
    inserted_user = insert_user(UserMock())
    assert type(inserted_user) is int


@patch("user_api.business.user.insert_user")
def test_insert_user_integrity_error(mock_insert_user):
    with pytest.raises(UserAlreadyInserted):
        insert_user(UserMock(raise_integrity_error=True))


@patch("user_api.business.user.update_user")
def test_update_user_sucess(mock_update_user):
    updated_user = update_user(id_user=1, update_data=UserMock().to_dict())
    assert updated_user is True
