from fastapi import APIRouter, Path, Body

from order_api.business import order

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
    "{index}/{doc_type}/{id}",
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
    "{index}/{doc_type}/{id}",
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
