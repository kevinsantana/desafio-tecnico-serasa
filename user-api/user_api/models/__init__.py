from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    next: str = Field(..., description="Next page with results")
    previous: str = Field(..., description="Previous page with results")
    first: str = Field(..., description="First page containing results")
    last: str = Field(..., description="Last page containing results")
    total: int = Field(..., description="Total number of pages")


class ErrorDetails(BaseModel):
    unique_id: str = Field(
        str(uuid4()),
        description="Unique identifier of the error. Can be used to trace the propagation of the error.",
    )
    message: str = Field(
        "CPF is a mandatory field.",
        description="Error description.",
    )


class Message(BaseModel):
    status: int = Field(400, description="HTTP status")
    error: str = Field("Bad Request", description="HTTP status description")
    message: str = Field(
        "CPF is a mandatory field",
        description="Error description.",
    )
    error_details: Optional[List[ErrorDetails]]


DEFAULT_RESPONSES = [
    Message(
        status=422,
        error="Unprocessable Entity",
        message="Invalid parameters",
        error_details=[ErrorDetails(message="CPF is a mandatory field")],
    ),
    Message(
        status=500,
        error="Internal Server Error",
        message="Error on our severs",
        error_details=[ErrorDetails(message="Internal error server")],
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
