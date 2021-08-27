from order_api.database.order import Order


def insert_order(order_data: dict, index: str, doc_type: str, id: int):
    return Order(**order_data).insert(
        type="create", id=id, index=index, doc_type=doc_type
    )
