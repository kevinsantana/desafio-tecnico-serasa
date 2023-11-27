import json
from collections import defaultdict

from order_api.database.order import Order
from order_api.services.user import get_user_by_id

from order_api.services.redis import redis
from order_api.exceptions import ErrorDetails
from order_api.exceptions.redis import RedisException

from loguru import logger


def _format_orders(hits: list):
    """
    Auxiliary function for generating order and user output data. Saves in the
    redis if one of the users has already been queried from the user-api microservice,
    also retrieving from redis if the data already exists.

    :param list hits: Output from the `search` method of the elasticsearch api.
    :raises RedisException: If redis is not available when saving or retrieving data.
    :return: Dictionary formatted with requests.
    :rtype: dict
    """
    orders = defaultdict(list)
    for hit in hits:
        user_id = hit.get("_source").get("user_id")
        user_info = get_user_by_id(user_id).get("result")
        if not redis.set(user_id, json.dumps(user_info)):
            raise RedisException(
                status=503,
                error="Service Unavailable",
                message="Service Unavailable",
                error_details=[
                    ErrorDetails(
                        message="One or more services are not available"
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


def insert_order(order_data: dict, index: str, doc_type: str, id: str):
    """
    Enters a new request, checking that the user entered exists in the microservice
    user-api.

    :param dict order_data: Order data.
    :param str index: Index in which the document will be inserted, by default in the
        'orders' index.
    :param str doc_type: Document type of the inserted document, by default 'order' index.
    :param str id: Id of the inserted document.
    """
    get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).insert(id=id, index=index, doc_type=doc_type).get("_id")


def get_order_by_id(index: str, doc_type: str, id: str):
    """
    Retrieves a base request based on its id.

    :param str index: Index at which the document will be inserted, by default in the index
        'orders'.
    :param str doc_type: Document type of the inserted document, by default 'order'.
    :param str id: Id of the document consulted.
    """
    return Order().list_one(id, index, doc_type).get("_source")


def update_order(order_data: dict, index: str, doc_type: str, id: str):
    """
    Updates an order.

    :param dict order_data: Order data to be updated.
    :param str index: Index at which the document will be inserted, by default in the index
        'orders'.
    :param str doc_type: Document type of the inserted document, by default 'order'.
    :param str id: Id of the updated document.
    """
    if order_data.get("user_id"):
        get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).update(id, index, doc_type).get("_version")


def delete_order(index: str, doc_type: str, id: int):
    """
    Deletes an order.

    :param str index: Index at which the document will be inserted, by default in the index
        'orders'.
    :param str doc_type: Document type of the inserted document, by default 'order'.
    :param str id: Id of the deleted document.
    """
    return Order().delete(id, index, doc_type).get("result")


def list_orders(
    user_id: str = None,
    quantity: int = 10,
    page: int = 0,
    index: str = "orders",
    doc_type: str = "order",
):
    """
    Lists all requests from the database, whether or not filtering by user. Format the output
    as standard in the file `architecture/er/nosql/order_output.json`.

    :param user_id: Filter requests based on the user id.
    :type user_id: str, optional.
    :param int quantity: Number of records per page.
    :param int page: Return page.
    :param index: Index at which the document will be inserted, by default in the index
        'orders'.
    :type index: str, optional
    :param doc_type: Document type of the inserted document, by default 'order'.
    :type doc_type: str, optional
    """
    query = None
    if user_id:
        get_user_by_id(user_id)
        query = {"user_id": str(user_id)}
    orders, total = Order().list_all(
        query=query,
        quantity=quantity,
        page=page,
        index=index,
        doc_type=doc_type,
    )
    logger.debug(orders)
    logger.debug(total)
    return _format_orders(orders), total
