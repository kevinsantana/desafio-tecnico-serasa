from fastapi import APIRouter, Body, Query

from user_api.business import user as usr
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

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    summary="Insere um usuário",
    response_model=UserCreateResponse,
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
    id_user: int = Query(1, description="Id do usuário a ser atualizado"),
    user_data: UserUpdateRequest = Body(..., description="Dados da atualização"),
):
    """
    Atualiza um usuário.
    """
    return {"update": usr.update_user(id_user=id_user, update_data=user_data.dict())}
