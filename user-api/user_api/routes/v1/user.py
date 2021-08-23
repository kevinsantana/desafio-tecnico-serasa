from fastapi import APIRouter, Body

from user_api.business import user as usr
from user_api.models.user import (
    UserRequest,
    UserResponse,
    USER_REGISTER_DEFAULT_RESPONSES,
)


router = APIRouter()


@router.post(
    "/",
    status_code=201,
    summary="Insere um usuário",
    response_model=UserResponse,
    responses=USER_REGISTER_DEFAULT_RESPONSES,
)
def create(
    user_data: UserRequest = Body(
        ..., description="Dados básicos para cadastro do usuárip"
    )
):
    """
    Endpoint para efetuar a gravação de um usuário no banco de dados.
    """
    return {"result": [usr.insert_user(**user_data.dict())]}
