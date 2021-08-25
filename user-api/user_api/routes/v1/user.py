import json

from fastapi import APIRouter, Body, Query, Request
from loguru import logger

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
from user_api.models.user import(
    UserDeleteResponse,
    USER_DELETE_DEFAULT_RESPONSES
)
from user_api.models.user import (
    ListUsersResponse, USER_LIST_DEFAULT_RESPONSES
)

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    summary="Insere um usuário",
    # response_model=UserCreateResponse,
    responses=USER_CREATE_DEFAULT_RESPONSES,
)
def create(
    user_data: UserCreateRequest = Body(
        ..., description="Dados básicos para cadastro do usuárip"
    )
):
    """
    Endpoint para efetuar a gravação de um usuário no banco de dados.
    """
    return {"id_user": usr.insert_user(usr_entity(**user_data.dict()))}


@router.put(
    "/{id_user}",
    status_code=200,
    summary="Atualizar um usuário",
    response_model=UserUpdateResponse,
    responses=USER_UPDATE_DEFAULT_RESPONSES,
)
def update(
    id_user: int = Query(..., description="Id do usuário a ser atualizado"),
    user_data: UserUpdateRequest = Body(..., description="Dados da atualização"),
):
    """
    Atualiza um usuário.
    """
    return {"result": usr.update_user(id_user=id_user, update_data=user_data.dict())}


@router.delete(
    "/{id_user}",
    status_code=200,
    summary="Deleta um usuário",
    response_model=UserDeleteResponse,
    responses=USER_DELETE_DEFAULT_RESPONSES,
)
def delete(
    id_user: int = Query(..., description="Id do usuário a ser deletado"),
):
    """
    Deleta um usuário
    """
    return {"result": usr.delete_user(id_user)}


@router.get(
    "/{id_user}",
    status_code=200,
    summary="Listar as informações de um usuário",
    response_model="",
    responses="",
)
def list_one(
    id_user: int = Query(..., description="Id do usuário"),
):
    """
    Lista um usuário
    """
    return {"result": usr.list_one(id_user)}


@router.get(
    "/",
    response_model=ListUsersResponse,
    status_code=200,
    summary="Listar as informações de todos os usuários",
    responses=USER_LIST_DEFAULT_RESPONSES,
)
def list_all(
    request: Request,
    quantity: int = Query(10, description="Quantidade de registros de retorno", gt=0),
    page: int = Query(1, description="Página atual de retorno", gt=0),
):
    """
    Lista as todos os usuários, paginando o resultado.
    """
    users, total = usr.list_all(quantity, page)
    return pagination(users, quantity, page, total, str(request.url))
