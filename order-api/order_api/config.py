from enum import Enum
from typing import Optional

from pydantic import BaseSettings


class EnvironmentEnum(Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"


class Envs(BaseSettings):
    DB_USER: str = "orderapi"
    DB_PASS: str = "orderapi"
    DB_HOST: str = "db_orders"
    DB_PORT: str = 9200
    INDEX_NAME: str = "orders"
    DB_URL = f"http://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{INDEX_NAME}"
    ENVIRONMENT: Optional[Enum] = EnvironmentEnum.PROD
    USER_API_ADDRESS: str = "http://user_api:7000"

    class Config:
        case_sensitive = True


envs = Envs()
