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
    Função auxiliar para gerar os dados de saída de pedidos e usuários. Grava no
    redis caso um dos usuários já tenham sido consultados do microsserviço user-api,
    recuperando também do redis caso o dado já exista.

    :param list hits: Saída do método `search` da api do elasticsearch.
    :raises RedisException: Se ao gravar ou recuperar um dado o redis não esteja
    disponível.
    :return: Dicionário formatado com os pedidos.
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
                message="Serviço indisponível",
                error_details=[
                    ErrorDetails(
                        message="Um ou mais serviços não estão disppníveis"
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
    Insere um novo pedido, verificando se o usuário informado existe no microsserviço
    user-api.

    :param dict order_data: Dados do pedido.
    :param str index: Indice no qual o documento será inserido, por padrão no índice
    'orders'.
    :param str doc_type: Document type do documento inserido, por padrão 'order'.
    :param str id: Id do documento inserido.
    """
    get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).insert(id=id, index=index, doc_type=doc_type).get("_id")


def get_order_by_id(index: str, doc_type: str, id: str):
    """
    Recupera um pedido da base a partir do seu id.

    :param str index: Indice no qual o documento será inserido, por padrão no índice
    'orders'.
    :param str doc_type: Document type do documento inserido, por padrão 'order'.
    :param str id: Id do documento consultado.
    """
    return Order().list_one(id, index, doc_type).get("_source")


def update_order(order_data: dict, index: str, doc_type: str, id: str):
    """
    Atualiza um pedido.

    :param dict order_data: Dados do pedido a serem atualizados.
    :param str index: Indice no qual o documento será inserido, por padrão no índice
    'orders'.
    :param str doc_type: Document type do documento inserido, por padrão 'order'.
    :param str id: Id do documento atualizado..
    """
    if order_data.get("user_id"):
        get_user_by_id(order_data.get("user_id"))
    return Order(**order_data).update(id, index, doc_type).get("_version")


def delete_order(index: str, doc_type: str, id: int):
    """
    Deleta um pedido.

    :param str index: Indice no qual o documento será inserido, por padrão no índice
    'orders'.
    :param str doc_type: Document type do documento inserido, por padrão 'order'.
    :param str id: Id do documento deletado.
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
    Lista todos os pedidos da base, filtrando ou não por usuário. Formata a saída
    conforme padrão no arquivo `architecture/er/nosql/order_output.json`.

    :param user_id: Filtro dos pedidos a partir do id do usuário.
    :type user_id: str, optional.
    :param int quantity: Quantidade de registros por página.
    :param int page: Página do retorno.
    :param index: Indice no qual o documento será inserido, por padrão no índice
    'orders'.
    :type index: str, optional
    :param doc_type: Document type do documento inserido, por padrão 'order'.
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
