from fastapi import APIRouter, Path, Body, Request, Query

from order_api.business import order
from order_api.routes.v1 import pagination

from order_api.models.order import IndexType, DocType
from order_api.models.order import (
    InsertOrderRequest,
    InsertOrderResponse,
    INSERT_ORDER_DEFAULT_RESPONSES,
)
from order_api.models.order import GetOrderResponse, GET_ORDER_DEFAULT_RESPONSES
from order_api.models.order import (
    UpdateOrderRequest,
    UpdateOrderResponse,
    UPDATE_ORDER_DEFAULT_RESPONSES,
)
from order_api.models.order import LIST_ORDERS_BY_USER_ID_DEFAULT_RESPONSES
from order_api.models.order import ListOdersResponse, LIST_ORDERS_DEFAULT_RESPONSES
from order_api.models.order import DeleteOrderResponse, DELETE_ORDER_DEFAULT_RESPONSES

router = APIRouter()


@router.post(
    "/{index}/{doc_type}/{id}",
    status_code=201,
    summary="Insere um novo pedido",
    response_model=InsertOrderResponse,
    responses=INSERT_ORDER_DEFAULT_RESPONSES,
)
def create(
    index: IndexType = Path(..., description="Index do pedido"),
    doc_type: DocType = Path(..., description="Document type do pedido"),
    id: int = Path(..., description="Id do pedido"),
    order_data: InsertOrderRequest = Body(
        ..., description="Dados básicos para cadastro do pedido"
    ),
):
    """
    Cria um novo pedido.
    """
    return {
        "id": order.insert_order(
            order_data=order_data.dict(),
            index=index,
            doc_type=doc_type,
            id=id,
        )
    }


@router.get(
    "/{index}/{doc_type}/{id}",
    status_code=200,
    summary="Recupera um pedido a partir do seu identificador",
    response_model=GetOrderResponse,
    responses=GET_ORDER_DEFAULT_RESPONSES,
)
def list_one_by_id(
    index: IndexType = Path(..., description="Index do pedido"),
    doc_type: DocType = Path(..., description="Document type do pedido"),
    id: int = Path(..., description="Id do pedido"),
):
    """
    Recupera um pedido a partir do seu id.
    """
    return {"result": order.get_order_by_id(index=index, doc_type=doc_type, id=id)}


@router.put(
    "/{index}/{doc_type}/{id}",
    status_code=200,
    summary="Atualizar um pedido",
    response_model=UpdateOrderResponse,
    responses=UPDATE_ORDER_DEFAULT_RESPONSES,
)
def update(
    index: IndexType = Path(..., description="Index do pedido"),
    doc_type: DocType = Path(..., description="Document type do pedido"),
    id: int = Path(..., description="Id do pedido"),
    order_data: UpdateOrderRequest = Body(
        ..., description="Dados para atualização do pedido"
    ),
):
    """
    Atualiza um pedido.
    """
    return {
        "version": order.update_order(
            order_data=order_data.dict(),
            index=index,
            doc_type=doc_type,
            id=id,
        )
    }


@router.delete(
    "/{index}/{doc_type}/{id}",
    status_code=200,
    summary="Deletar um pedido",
    response_model=DeleteOrderResponse,
    responses=DELETE_ORDER_DEFAULT_RESPONSES,
)
def delete(
    index: IndexType = Path(..., description="Index do pedido"),
    doc_type: DocType = Path(..., description="Document type do pedido"),
    id: int = Path(..., description="Id do pedido"),
):
    """
    Deleta um pedido
    """
    return {"result": order.delete_order(index, doc_type, id)}


@router.get(
    "/{index}/{doc_type}/",
    status_code=200,
    summary="Listar todos os pedidos",
    response_model=ListOdersResponse,
    responses=LIST_ORDERS_DEFAULT_RESPONSES,
)
def get_orders(
    request: Request,
    quantity: int = Query(10, description="Quantidade de registros de retorno", gt=0),
    page: int = Query(1, description="Página atual de retorno", gt=0),
    index: IndexType = Path(..., description="Index do pedido"),
    doc_type: DocType = Path(..., description="Document type do pedido"),
):
    """
    Listar todos os pedidos, paginando o resultado.
    """
    orders, total = order.list_orders(
        quantity=quantity,
        page=page,
        index=index,
        doc_type=doc_type,
    )
    return pagination(orders, quantity, page, total, str(request.url))


@router.get(
    "/{user_id}",
    status_code=200,
    summary="Listar todos os pedidos por id do usuário",
    response_model=ListOdersResponse,
    responses=LIST_ORDERS_BY_USER_ID_DEFAULT_RESPONSES,
)
def get_orders_by_user_id(
    request: Request,
    quantity: int = Query(10, description="Quantidade de registros de retorno", gt=0),
    page: int = Query(1, description="Página atual de retorno", gt=0),
    user_id: int = Query(1, description="Id do usuário associado ao pedido")
):
    """
    Listar todos os pedidos filtrando o resultado por id do usuário e paginando
    o resultado.
    """
    orders, total = order.list_orders(
        user_id=user_id,
        quantity=quantity,
        page=page
    )
    return pagination(orders, quantity, page, total, str(request.url))
