from fastapi import APIRouter

from user_api.routes.v1 import user


v1 = APIRouter()

v1.include_router(user.router, prefix="/user", tags=["users"])
