import os
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, BaseSettings, PostgresDsn, validator


class EnvironmentEnum(Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"


class DatabaseModel(BaseModel):
    DATABASE_USER: str = "userapi"
    DATABASE_PASS: str = "userapi"
    DATABASE_HOST: str = "db_user"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "userapi"
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    @validator("DATABASE_URL", pre=True)
    def make_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return PostgresDsn.build(
            scheme="postgresql",
            user=values["DATABASE_USER"],
            password=values["DATABASE_PASS"],
            host=values["DATABASE_HOST"],
            port=values["DATABASE_PORT"],
            path=f"/{values['DATABASE_NAME']}",
        )


class Envs(BaseSettings):
    ENVIRONMENT: Optional[Enum] = EnvironmentEnum.PROD
    RESET_DB: Optional[bool] = False
    SQLALCHEMY_ECHO: bool = True
    SQLALCHEMY_TEST: str = "sqlite:///./sql_app.db"
    SQLALCHEMY_DB_URI: str = DatabaseModel().DATABASE_URL
    SQLALCHEMY_URI: str = SQLALCHEMY_TEST if ENVIRONMENT == EnvironmentEnum.LOCAL else SQLALCHEMY_DB_URI
    SECRET_KEY: str = os.environ.get("SECRET_KEY", None)

    class Config:
        case_sensitive = True


envs = Envs()
