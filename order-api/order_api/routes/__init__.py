from fastapi import APIRouter

from order_api.routes.v1 import order


v1 = APIRouter()

v1.include_router(order.router, prefix="/orders", tags=["orders"])
