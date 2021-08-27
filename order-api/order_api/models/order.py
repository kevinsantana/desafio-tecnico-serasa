from typing import Optional, List

from pydantic import BaseModel, Field
from user_api.exceptions import ErrorDetails

from user_api.models import Message, parse_openapi, Pagination


class InsertOrderRequest(BaseModel):
    user_id: int = Field(1, description="Id do usuário associado ao pedido")
    item_description: str = Field("Um item incrivel", description="Descrição do item")
    item_quantity: int = Field(3, description="Quantidade de itens")
    item_price: float = Field(2.50, description="Valor do item")
    total_value: float = Field(7.50, description="Valor total do pedido")


class InsertOrderResponse(BaseModel):
    id: int


INSERT_ORDER_DEFAULT_RESPONSES = parse_openapi([])
