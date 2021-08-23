from decimal import Decimal
from datetime import datetime
from collections import UserDict
from typing import Generator, TypeVar, Iterable

from loguru import logger

from sqlalchemy import asc, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from user_api.config import envs
# from user_api.exceptions.database import UpdateTableException

Base = declarative_base()

engine = create_engine(
    envs.SQLALCHEMY_URI,
    pool_pre_ping=True,
    # connect_args={"check_same_thread": False},
    echo=envs.SQLALCHEMY_ECHO,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

str_or_bool = TypeVar("str_or_bool", str, bool)


class MyDict(UserDict):
    pass


class DatabaseService:
    def __init__(self):
        logger.info(f"db url {envs.SQLALCHEMY_URI}")
        self._sessao = SessionLocal()

    @property
    def query(self):
        return self._sessao.query

    @property
    def add(self):
        return self._sessao.add

    @property
    def remove(self):
        return self._sessao.delete

    @property
    def bulk_insert(self):
        return self._sessao.bulk_save_objects

    def commit(self):
        self._sessao.commit()

    def __enter__(self):
        return self

    def __exit__(self, except_type, except_value, except_table):
        if except_type and issubclass(except_type, Exception):
            logger.error(f"{except_type}: {except_value}")
            self._sessao.rollback()
        self._sessao.close()


class DataBaseCrud:
    parser: dict = None

    @classmethod
    def list_one(
        cls,
        connection: DatabaseService,
        filter: tuple = None,
        order_by: tuple = None,
    ):
        query = connection.query(cls)

        if filter:
            query = query.filter(*filter)

        if order_by:
            query = (
                query.order_by(asc(getattr(cls, order_by[0])))
                if "asc" in order_by[1]
                else query.order_by(desc(getattr(cls, order_by[0])))
            )

        return query.first()

    @classmethod
    def find_all(
        cls,
        connection: DatabaseService,
        after: int = 0,
        limit: int = 100,
        is_active: str_or_bool = True,
    ) -> Generator:
        query = connection.query(cls)

        if "is_active" in dir(cls) and is_active != "all":
            query = query.filter(*(cls.is_active == is_active,))

        yield from query.offset(after).limit(limit)

    @classmethod
    def search(
        cls,
        connection: DatabaseService,
        filter: tuple = None,
        after: int = 0,
        limit: int = 100,
        is_active: str_or_bool = True,
        order_by: tuple = None,
    ) -> Generator:
        query = connection.query(cls)

        if "is_active" in dir(cls) and is_active != "all":
            filter = (*filter, cls.is_active == is_active)

        if filter:
            query = query.filter(*filter)

        if order_by:
            query = (
                query.order_by(asc(getattr(cls, order_by[0])))
                if "asc" in order_by[1]
                else query.order_by(desc(getattr(cls, order_by[0])))
            )

        if after != -1:
            query = query.offset(after).limit(limit)

        yield from query

    @classmethod
    def join(cls, connection: DatabaseService, table: "DataBaseCrud"):
        return connection.query(cls).join(table)

    @classmethod
    def update(cls, connection: DatabaseService, filter: tuple, data: dict) -> int:
        updated_list = list()
        for register in cls.search(
            connection, filter=filter, after=-1, is_active="all"
        ):
            for column, value in data.items():
                try:
                    getattr(register, column)
                    setattr(register, column, value)
                except AttributeError:
                    raise Exception(
                        f"Coluna {column} não encontrada na tabela {register}"
                    )
            updated_list.append(register)

        connection.commit()

        return updated_list

    def insert(self, connection: DatabaseService):
        connection.add(self)
        connection.commit()
        return self

    @classmethod
    def _before_bulk_insert(cls, iterable, *args, **kwargs):
        pass

    @classmethod
    def _after_bulk_insert(cls, iterable, *args, **kwargs):
        pass

    @classmethod
    def bulk_insert(
        cls,
        connection: DatabaseService,
        iterable: Iterable,
        commit: bool = True,
        *args,
        **kwargs,
    ) -> Iterable:
        cls._before_bulk_insert(iterable)
        models_objs = []
        for data in iterable:
            if not isinstance(data, cls):
                data = cls(**data)
            models_objs.append(data)
        connection.bulk_insert(models_objs)
        if commit:
            connection.commit()
        cls._after_bulk_insert(iterable)
        return models_objs

    def delete(self, connection: DatabaseService):
        connection.remove(self)
        connection.commit()

    def __parse_table(
        self, no_fk: bool = True, no_none: bool = True, no_id: bool = True
    ):
        class_attr_dict = dict()
        for attr in self.__table__.columns:
            if no_fk and attr.name.startswith("fk"):
                continue
            if no_id and attr.name.startswith("id"):
                continue
            attr_value = getattr(self, attr.name)
            if no_none and attr_value is None:
                continue
            if type(attr_value) is datetime:
                attr_value = attr_value.strftime("%Y-%m-%d")
            elif type(attr_value) is Decimal:
                attr_value = float(attr_value)
            else:
                attr_value = str(attr_value)
            class_attr_dict[attr.name] = attr_value
        return class_attr_dict

    def to_dict(self, no_fk: bool = True, no_none: bool = True, no_id: bool = True):
        return self.__parse_table(no_fk, no_none, no_id)

    def __repr__(self):
        return f"{type(self).__qualname__}({self.to_dict()})"
