import json
from collections import defaultdict

from order_api.database.order import Order
from order_api.services.user import get_user_by_id

from order_api.services.redis import redis
from order_api.exceptions import ErrorDetails
from order_api.exceptions.redis import RedisException

from loguru import logger


def _format_orders(hits: list):
    orders = defaultdict(list)
    for hit in hits:
        user_id = hit.get("_source").get("user_id")
        user_info = get_user_by_id(user_id).get("result")
        if not redis.set(user_id, json.dumps(user_info)):
            raise RedisException(
                status=400,
                error="Bad Request",
                message="Um ou mais serviços não estão disppníveis",
                error_details=[
                    ErrorDetails(
                        message=f"Serviço indisponível"
                    ).to_dict()
                ],
            )
        orders["user"] = (
            json.loads(redis.get(user_id)) if redis.get(user_id) else user_info
        )
        orders["orders"].append(
            {
                "id": hit.get("_id"),
                "item_description": hit.get("_source").get("item_description"),
                "item_quantity": hit.get("_source").get("item_quantity"),
                "item_price": hit.get("_source").get("item_price"),
                "total_value": hit.get("_source").get("total_value"),
                "created_at": hit.get("_source").get("created_at"),
                "updated_at": hit.get("_source").get("updated_at"),
            }
        )
    return orders


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


def list_orders(
    quantity: int = 10, page: int = 0, index: str = "orders", doc_type: str = "order"
):
    """
    Find all orders
    """
    orders, total = Order().list_all(
        quantity=quantity,
        page=page,
        index=index,
        doc_type=doc_type,
    )
    logger.debug(orders)
    logger.debug(total)
    return _format_orders(orders), total
