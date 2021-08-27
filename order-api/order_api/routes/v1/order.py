from typing import Optional

from fastapi import APIRouter, Path, Body

from order_api.business import order

from order_api.models.order import (
    InsertOrderRequest,
    InsertOrderResponse,
    INSERT_ORDER_DEFAULT_RESPONSES,
)

router = APIRouter()


@router.post(
    "/{index}/{doc_type}/{id}",
    status_code=201,
    summary="Insere um novo pedido",
    response_model="",
    responses="",
)
def create(
    index: Optional[str] = Path(None, description="Index do pedido"),
    doc_type: Optional[str] = Path(None, description="Document type do pedido"),
    id: Optional[int] = Path(None, description="Id do pedido"),
    order_data: InsertOrderRequest = Body(
        ..., description="Dados básicos para cadastro do pedido"
    ),
):
    """
    Cria um novo pedido.
    """
    return {"id": order.insert_order(order_data.dict(), index, doc_type, id)}
