from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from order_api.exceptions import ErrorDetails

from order_api.models import Message, parse_openapi, Pagination


class IndexType(str, Enum):
    index = "orders"


class DocType(str, Enum):
    doc_type = "order"


class InsertOrderRequest(BaseModel):
    user_id: int = Field(1, description="User id")
    item_description: str = Field("An awesome item", description="Item description")
    item_quantity: int = Field(3, description="Size of the items")
    item_price: float = Field(2.50, description="Item value")
    total_value: float = Field(7.50, description="Order total amount")


class InsertOrderResponse(BaseModel):
    id: int


class GetOrder(BaseModel):
    user_id: int = Field(..., description="User id")
    item_description: str = Field(..., description="Item description")
    item_quantity: int = Field(..., description="Quantidade de itens")
    item_price: float = Field(..., description="Item value")
    total_value: float = Field(7.50, description="Order total amount")
    created_at: str = Field(..., description="Creation date of the order")
    updated_at: Optional[str] = Field(None, description="Order updated date")


class GetOrderResponse(BaseModel):
    result: GetOrder


class UpdateOrderRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="User id")
    item_description: Optional[str] = Field(None, description="Item description")
    item_quantity: Optional[int] = Field(None, description="Quantidade de itens")
    item_price: Optional[float] = Field(None, description="Item value")
    total_value: Optional[float] = Field(None, description="Order total amount")


class UpdateOrderResponse(BaseModel):
    version: int


class DeleteOrderResponse(BaseModel):
    result: str


class Order(BaseModel):
    id: str = Field(..., description="Id do pedido")
    item_description: str = Field(..., description="Item description")
    item_quantity: int = Field(..., description="Quantidade de itens")
    item_price: float = Field(..., description="Item value")
    total_value: float = Field(7.50, description="Order total amount")
    created_at: str = Field(..., description="Creation date of the order")
    updated_at: Optional[str] = Field(None, description="Order updated date")


class User(BaseModel):
    id_user: int = Field(..., description="User id")
    name: str = Field(..., description="Full name")
    cpf: str = Field(..., description="Cadastro de pessoa física(CPF)")
    email: Optional[str] = Field(..., description="E-mail")
    phone_number: str = Field(..., description="Phone number")
    created_at: str = Field(..., description="User creation date")
    updated_at: Optional[str] = Field(None, description="User updated date")


class ListOrders(BaseModel):
    user: User
    orders: List[Order]


class ListOdersResponse(BaseModel):
    result: ListOrders
    pagination: Pagination = Field(..., description="Pagination data")


INSERT_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=409,
            error="Conflict",
            message="Repeated data",
            error_details=[ErrorDetails(message="Order id is repeated").to_dict()],
        ),
        Message(
            status=404,
            error="Not found",
            message="User not found",
            error_details=[ErrorDetails(message="User does not exist").to_dict()],
        ),
    ]
)

GET_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Order not found",
            error_details=[ErrorDetails(message="The order does not exist").to_dict()],
        ),
    ]
)

UPDATE_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Order not found",
            error_details=[ErrorDetails(message="The order does not exist").to_dict()],
        ),
        Message(
            status=404,
            error="Not found",
            message="User not found",
            error_details=[ErrorDetails(message="User does not exist").to_dict()],
        ),
        Message(
            status=400,
            error="Bad Request",
            message="Invalid field",
            error_details=[
                ErrorDetails(message="The required field does not exist").to_dict()
            ],
        ),
    ]
)


DELETE_ORDER_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not found",
            message="Order not found",
            error_details=[ErrorDetails(message="The order does not exist").to_dict()],
        ),
    ]
)

LIST_ORDERS_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=503,
            error="Service Unavailable",
            message="Serviço indisponível",
            error_details=[
                ErrorDetails(
                    message="One or more services are unavailable at the moment"
                ).to_dict()
            ],
        ),
    ]
)


LIST_ORDERS_BY_USER_ID_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=400,
            error="Bad request",
            message="Malformed query",
            error_details=[ErrorDetails(message="Malformed query").to_dict()],
        ),
    ]
)
