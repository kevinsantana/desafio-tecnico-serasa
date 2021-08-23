from typing import Optional

from pydantic import BaseModel, Field

from user_api.models import parse_openapi


# TODO: regex no e-mail
class UserRequest(BaseModel):
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


class UserResponse(BaseModel):
    result: bool


USER_REGISTER_DEFAULT_RESPONSES = parse_openapi([])
