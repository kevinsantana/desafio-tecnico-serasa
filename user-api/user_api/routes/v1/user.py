from fastapi import APIRouter, Body, Query, Request

from user_api.business import user as usr
from user_api.routes.v1 import pagination
from user_api.entities.user import User as usr_entity
from user_api.models.user import (
    UserCreateRequest,
    UserCreateResponse,
    USER_CREATE_DEFAULT_RESPONSES,
)
from user_api.models.user import (
    UserUpdateRequest,
    UserUpdateResponse,
    USER_UPDATE_DEFAULT_RESPONSES,
)
from user_api.models.user import UserDeleteResponse, USER_DELETE_DEFAULT_RESPONSES
from user_api.models.user import ListUsersResponse, USER_LIST_DEFAULT_RESPONSES

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    summary="Creates an user",
    response_model=UserCreateResponse,
    responses=USER_CREATE_DEFAULT_RESPONSES,
)
def create(
    user_data: UserCreateRequest = Body(
        ..., description="Basic data for user registration"
    )
):
    """
    Endpoint to save a user to the database.
    """
    return {"id_user": usr.insert_user(usr_entity(**user_data.dict()))}


@router.put(
    "/{id_user}",
    status_code=200,
    summary="Update an user",
    response_model=UserUpdateResponse,
    responses=USER_UPDATE_DEFAULT_RESPONSES,
)
def update(
    id_user: int = Query(..., description="User id to be updated"),
    user_data: UserUpdateRequest = Body(..., description="Data to be updated"),
):
    """
    Updates an user.
    """
    return {"result": usr.update_user(id_user=id_user, update_data=user_data.dict())}


@router.delete(
    "/{id_user}",
    status_code=200,
    summary="Deletes an user",
    response_model=UserDeleteResponse,
    responses=USER_DELETE_DEFAULT_RESPONSES,
)
def delete(
    id_user: int = Query(..., description="User id to be deleted"),
):
    """
    Deletes an user
    """
    return {"result": usr.delete_user(id_user)}


@router.get(
    "/{id_user}",
    status_code=200,
    summary="Get an user",
    response_model="",
    responses="",
)
def list_one(
    id_user: int = Query(..., description="User id"),
):
    """
    Get an user
    """
    return {"result": usr.list_one(id_user)}


@router.get(
    "/",
    response_model=ListUsersResponse,
    status_code=200,
    summary="List users",
    responses=USER_LIST_DEFAULT_RESPONSES,
)
def list_all(
    request: Request,
    quantity: int = Query(10, description="Number of return records", gt=0),
    page: int = Query(1, description="Current return page", gt=0),
):
    """
    List all users, paginating the result.
    """
    users, total = usr.list_all(quantity, page)
    return pagination(users, quantity, page, total, str(request.url))
