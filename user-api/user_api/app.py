import time
import json
import urllib3
from uuid import uuid1, uuid4
from datetime import datetime

from loguru import logger
from fastapi import FastAPI
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from user_api import __version__
from user_api.routes import v1
from user_api.files import html_desc
from user_api.routes.v1 import doc_sphinx
from user_api.exceptions import UserApiException
from user_api.database.create_database import create_database
from docs import (
    build_html_pages,
    build_html_static,
    build_html_source,
)

urllib3.disable_warnings()

logger.level("REQUEST RECEBIDA", no=38, color="<yellow>")
logger.level("REQUEST FINALIZADA", no=39, color="<yellow>")
logger.level("EXCEPTION", no=38, color="<yellow>")


def include_router(app: FastAPI):
    app.include_router(v1, prefix="/v1")


def configure_static(app: FastAPI):
    app.include_router(doc_sphinx.router)
    app.mount("/pages", StaticFiles(directory=build_html_pages), name="pages")
    app.mount("/_static", StaticFiles(directory=build_html_static), name="static")
    app.mount("/_sources", StaticFiles(directory=build_html_source), name="sources")


def load_exceptions(app: FastAPI):
    @app.exception_handler(UserApiException)
    async def hub_payments_exception_handler(
        request: Request, exception: UserApiException
    ):  # pragma: no cover
        return JSONResponse(
            status_code=exception.status,
            content={
                "timestamp": str(datetime.now()),
                "status": exception.status,
                "error": exception.error,
                "message": exception.message,
                "method": request.method,
                "path": request.url.path,
                "error_details": exception.error_details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exception: RequestValidationError
    ):  # pragma: no cover
        return JSONResponse(
            status_code=422,
            content={
                "timestamp": str(datetime.now()),
                "status": 422,
                "error": "Unprocessable Entity",
                "message": "Os parâmetros da requisição estão inválidos",
                "method": request.method,
                "path": request.url.path,
                "error_details": {
                    "unique_id": str(uuid4()),
                    "message": json.loads(exception.json()),
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exception: HTTPException
    ):  # pragma: no cover
        message = {
            401: "Não autorizado",
            404: "Endereço não encontrado",
            405: "Método não permitido",
        }
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "timestamp": str(datetime.now()),
                "status": exception.status_code,
                "error": message[exception.status_code],
                "message": message[exception.status_code],
                "method": request.method,
                "path": request.url.path,
                "error_details": {
                    "unique_id": str(uuid4()),
                    "message": message[exception.status_code],
                },
            },
        )


def http_middleware(app: FastAPI):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):  # pragma: no cover
        requets_id = uuid1()

        logger.log(
            "REQUEST RECEBIDA",
            f"[{request.method}] ID: {requets_id} - IP: {request.client.host}"
            + f" - ENDPOINT: {request.url.path}",
        )

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.log(
            "REQUEST FINALIZADA",
            f"[{request.method}] ID: {requets_id} - IP: {request.client.host}"
            + f" - ENDPOINT: {request.url.path} - TEMPO: {process_time}",
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response


def start_application():
    app = FastAPI(
        title="USER-API",
        description=open(html_desc).read(),
        version=__version__,
        docs_url="/v1/swagger",
        redoc_url="/v1/docs",
    )
    include_router(app)
    configure_static(app)
    load_exceptions(app)
    http_middleware(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_credentials=True,
        allow_headers=["*"],
    )
    create_database(reset=False)
    return app
