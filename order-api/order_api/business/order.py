from order_api.database.order import Order
from order_api.services.user import get_user_by_id

from order_api.exceptions import ErrorDetails
from order_api.exceptions.order import (
    UserNotFoundException,
    OrderNotFoundException
)

from loguru import logger


def insert_order(order_data: dict, index: str, doc_type: str, id: int):
    """
    Insert order
    """
    get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).insert(id=id, index=index, doc_type=doc_type).get("_id")


def get_order_by_id(index: str, doc_type: str, id: int):
    """
    Get order
    """
    return Order().list_one(id, index, doc_type).get("_source")


def update_order(order_data: dict, index: str, doc_type: str, id: int):
    """
    Update order
    """
    if order_data.get("user_id"):
        get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).update(id, index, doc_type).get("_version")


def delete_order(index: str, doc_type: str, id: int):
    """
    Delete order
    """
    return Order().delete(id, index, doc_type).get("result")
