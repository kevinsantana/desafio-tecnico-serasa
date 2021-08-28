from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from order_api.exceptions import ErrorDetails

from order_api.models import Message, parse_openapi


class IndexType(str, Enum):
    index = "orders"


class DocType(str, Enum):
    doc_type = "order"


class InsertOrderRequest(BaseModel):
    user_id: int = Field(1, description="Id do usuário associado ao pedido")
    item_description: str = Field("Um item incrivel", description="Descrição do item")
    item_quantity: int = Field(3, description="Quantidade de itens")
    item_price: float = Field(2.50, description="Valor do item")
    total_value: float = Field(7.50, description="Valor total do pedido")


class InsertOrderResponse(BaseModel):
    id: int


class GetOrder(BaseModel):
    user_id: int = Field(..., description="Id do usuário associado ao pedido")
    item_description: str = Field(..., description="Descrição do item")
    item_quantity: int = Field(..., description="Quantidade de itens")
    item_price: float = Field(..., description="Valor do item")
    created_at: str = Field(..., description="Data de criação do pedido")
    updated_at: Optional[str] = Field(None, description="Data de alteração do pedido")


class GetOrderResponse(BaseModel):
    result: GetOrder


class UpdateOrderRequest(BaseModel):
    user_id: Optional[int] = Field(
        None, description="Id do usuário associado ao pedido"
    )
    item_description: Optional[str] = Field(None, description="Descrição do item")
    item_quantity: Optional[int] = Field(None, description="Quantidade de itens")
    item_price: Optional[float] = Field(None, description="Valor do item")
    total_value: Optional[float] = Field(None, description="Valor total do pedido")


class UpdateOrderResponse(BaseModel):
    version: int


class DeleteOrderResponse(BaseModel):
    result: str


INSERT_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=409,
            error="Conflict",
            message="Dado repetido",
            error_details=[ErrorDetails(message="O id do pedido é repetido").to_dict()],
        ),
        Message(
            status=404,
            error="Not found",
            message="Usuário não encontrado",
            error_details=[
                ErrorDetails(message="O usuário informado não existe na base").to_dict()
            ],
        ),
    ]
)

GET_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Pedido não encontrado",
            error_details=[
                ErrorDetails(message="O pedido informado não existe na base").to_dict()
            ],
        ),
    ]
)

UPDATE_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Pedido não encontrado",
            error_details=[
                ErrorDetails(message="O pedido informado não existe na base").to_dict()
            ],
        ),
        Message(
            status=404,
            error="Not found",
            message="Usuário não encontrado",
            error_details=[
                ErrorDetails(message="O usuário informado não existe na base").to_dict()
            ],
        ),
        Message(
            status=400,
            error="Bad Request",
            message="Campo de atualização inválido",
            error_details=[
                ErrorDetails(
                    message="O campo informado para atualização não existe"
                ).to_dict()
            ],
        ),
    ]
)


DELETE_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Pedido não encontrado",
            error_details=[
                ErrorDetails(message="O pedido informado não existe na base").to_dict()
            ],
        ),
    ]
)
