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
    summary="Insert a new order",
    response_model=InsertOrderResponse,
    responses=INSERT_ORDER_DEFAULT_RESPONSES,
)
def create(
    index: IndexType = Path(..., description="Order index"),
    doc_type: DocType = Path(..., description="Request document type"),
    id: int = Path(..., description="Order id"),
    order_data: InsertOrderRequest = Body(
        ..., description="Basic data for order registration"
    ),
):
    """
    Create a new order.
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
    summary="Retrieves a request from its identifier",
    response_model=GetOrderResponse,
    responses=GET_ORDER_DEFAULT_RESPONSES,
)
def list_one_by_id(
    index: IndexType = Path(..., description="Order index"),
    doc_type: DocType = Path(..., description="Request document type"),
    id: int = Path(..., description="Order id"),
):
    """
    Retrieves an order from its id.
    """
    return {"result": order.get_order_by_id(index=index, doc_type=doc_type, id=id)}


@router.put(
    "/{index}/{doc_type}/{id}",
    status_code=200,
    summary="Update an order",
    response_model=UpdateOrderResponse,
    responses=UPDATE_ORDER_DEFAULT_RESPONSES,
)
def update(
    index: IndexType = Path(..., description="Order index"),
    doc_type: DocType = Path(..., description="Request document type"),
    id: int = Path(..., description="Order id"),
    order_data: UpdateOrderRequest = Body(..., description="Data for order update"),
):
    """
    Updates an order.
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
    summary="Delete an order",
    response_model=DeleteOrderResponse,
    responses=DELETE_ORDER_DEFAULT_RESPONSES,
)
def delete(
    index: IndexType = Path(..., description="Order index"),
    doc_type: DocType = Path(..., description="Request document type"),
    id: int = Path(..., description="Order id"),
):
    """
    Deletes an order.
    """
    return {"result": order.delete_order(index, doc_type, id)}


@router.get(
    "/{index}/{doc_type}/",
    status_code=200,
    summary="List all orders",
    response_model=ListOdersResponse,
    responses=LIST_ORDERS_DEFAULT_RESPONSES,
)
def get_orders(
    request: Request,
    quantity: int = Query(10, description="Quantity of returned records", gt=0),
    page: int = Query(1, description="Current return page", gt=0),
    index: IndexType = Path(..., description="Order index"),
    doc_type: DocType = Path(..., description="Request document type"),
):
    """
    List all requests, paginating the result.
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
    summary="List all orders by user id",
    response_model=ListOdersResponse,
    responses=LIST_ORDERS_BY_USER_ID_DEFAULT_RESPONSES,
)
def get_orders_by_user_id(
    request: Request,
    quantity: int = Query(10, description="Quantity of returned records", gt=0),
    page: int = Query(1, description="Current return page", gt=0),
    user_id: int = Query(1, description="User ID associated with the request"),
):
    """
    List all orders by filtering the result by user id and paginating
    the result.
    """
    orders, total = order.list_orders(user_id=user_id, quantity=quantity, page=page)
    return pagination(orders, quantity, page, total, str(request.url))
