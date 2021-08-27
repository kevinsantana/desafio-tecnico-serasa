from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    next: str = Field(..., description="Proxima página com resultados")
    previous: str = Field(..., description="Página anterior com resultados")
    first: str = Field(..., description="Primeira página que contem resultados")
    last: str = Field(..., description="Última página que contem resultados")
    total: int = Field(..., description="Quantidade total de páginas")


class ErrorDetails(BaseModel):
    unique_id: str = Field(
        str(uuid4()),
        description="Identificador único do erro. Pode ser utilizado para rastrear a propagação do erro.",
    )
    message: str = Field(
        "CPF é um campo obrigatório.",
        description="Descrição do erro.",
    )


class Message(BaseModel):
    status: int = Field(400, description="O status HTTP")
    error: str = Field("Bad Request", description="A descrição do status HTTP")
    message: str = Field(
        "CPF é um campo obrigatório",
        description="Mensagem resumindo o erro",
    )
    error_details: Optional[List[ErrorDetails]]


DEFAULT_RESPONSES = [
    Message(
        status=422,
        error="Unprocessable Entity",
        message="Os parâmetros da requisição estão inválidos!",
        error_details=[ErrorDetails(message="CPF é um campo obrigatório")],
    ),
    Message(
        status=500,
        error="Internal Server Error",
        message="Erro interno no servidor",
        error_details=[ErrorDetails(message="Ocorreu um erro interno")],
    ),
]


def parse_openapi(responses: list) -> dict:
    responses.extend(DEFAULT_RESPONSES)
    return {
        example.status: {
            "content": {"application/json": {"example": example.dict()}},
            "model": Message,
        }
        for example in responses
    }
