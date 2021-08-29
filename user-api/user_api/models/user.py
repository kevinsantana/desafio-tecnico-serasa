from typing import Optional, List

from pydantic import BaseModel, Field
from user_api.exceptions import ErrorDetails

from user_api.models import Message, parse_openapi, Pagination


# TODO: regex no e-mail
class UserCreateRequest(BaseModel):
    name: str = Field(
        "João Augusto Albuquerque",
        description="Nome completo",
        min_length=10,
        max_length=100,
    )
    cpf: str = Field(
        "000.000.000-00",
        description="Cadastro de pessoa física(CPF)",
        min_length=11,
        max_length=14,
        regex=r"\d",
    )
    email: Optional[str] = Field(
        "seuemail@mail.com", description="E-mail", min_length=6, max_length=55
    )
    phone_number: str = Field(
        "99999-9999",
        description="Número do telefone",
        min_length=9,
        max_length=10,
        regex=r"\d",
    )


class UserCreateResponse(BaseModel):
    id_user: int


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(
        "João Augusto Albuquerque",
        description="Nome completo",
        min_length=10,
        max_length=100,
    )
    cpf: Optional[str] = Field(
        "000.000.000-00",
        description="Cadastro de pessoa física(CPF)",
        min_length=11,
        max_length=14,
        regex=r"\d",
    )
    email: Optional[str] = Field(
        "seuemail@mail.com", description="E-mail", min_length=6, max_length=55
    )
    phone_number: Optional[str] = Field(
        "99999-9999",
        description="Número do telefone",
        min_length=9,
        max_length=10,
        regex=r"\d",
    )


class UserUpdateResponse(BaseModel):
    result: bool


class UserDeleteResponse(BaseModel):
    result: bool


class GetUserResponse(BaseModel):
    result: UserCreateRequest


class ListUsersResponse(BaseModel):
    result: List[UserCreateRequest]
    pagination: Pagination = Field(..., description="Dados de paginação")


USER_CREATE_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=409,
            error="Conflict",
            message="Dado repetido",
            error_details=[
                ErrorDetails(
                    message="Os dados informados para o usuário já existem na base"
                ).to_dict()
            ],
        ),
        Message(
            status=404,
            error="Not found",
            message="Senha de criptografia vazia",
            error_details=[
                ErrorDetails(
                    message="A senha de criptografia não pode ser vazia"
                ).to_dict()
            ],
        ),
    ]
)

USER_UPDATE_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not Found",
            message="Usuário não encontrado",
            error_details=[
                ErrorDetails(message="Erro ao atualizar o usuário").to_dict()
            ],
        ),
    ]
)

USER_DELETE_DEFAULT_RESPONSES = parse_openapi(
    [
        Message(
            status=404,
            error="Not Found",
            message="Usuário não encontrado",
            error_details=[ErrorDetails(message="Erro ao deletar o usuário").to_dict()],
        ),
    ]
)


USER_LIST_DEFAULT_RESPONSES = parse_openapi([])
