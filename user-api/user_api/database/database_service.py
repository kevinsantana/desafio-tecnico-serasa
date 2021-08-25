from decimal import Decimal
from datetime import datetime
from collections import UserDict
from typing import Generator, TypeVar

from loguru import logger

from sqlalchemy import asc, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from user_api.config import envs
from user_api.exceptions import ErrorDetails
from user_api.exceptions.database import UpdateTableException

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
    """
    Provides an API to interact with sqlalchemy.
    """

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
    """
    Provide an API to make basic database operations (crud).
    """

    @classmethod
    def list_one(
        cls,
        connection: DatabaseService,
        filter: tuple = None,
        order_by: tuple = None,
    ):
        """
        Find and return the first record on database with provided filter.

        :param connection: The connection to database.
        :param tuple filter: Filter to apply on query.
        :param tuple order_by: If the result query should be order in the given way.
        :return: Found record.
        :rtype: sqlalchemy.query
        """
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
        page: int = 0,
        quantity: int = 100,
        is_active: str_or_bool = True,
    ) -> Generator:
        """
        Find and return all records on database with given filter.

        :param connection: Connection to database.
        :param int page: Query offset.
        :param int quantity: Result quantity in returned page.
        :param bool is_active: Returns only active records with column 'is_active'.
        :return: Query result.
        :rtype: generator
        """
        query = connection.query(cls)

        if "is_active" in dir(cls) and is_active != "all":
            query = query.filter(*(cls.is_active == is_active,))

        offset = (page - 1) * quantity
        yield from query.limit(quantity).offset(offset)

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
        """
        Search for all records with given filter.

        :param connection: Connection to database.
        :param tuple filter: Filter to apply on query.
        :param int after: How many records should be skipped in result query.
        :param int limit: Result query limit.
        :param bool is_active: Returns only active records with column 'is_active'.
        :param tuple order_by: If the result query should be order in the given way.
        :return: Query result.
        :rtype: generator
        """
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
    def update(cls, connection: DatabaseService, filter: tuple, data: dict) -> list:
        """
        Update a given record on database.

        :param connection: Connection to database.
        :param tuple filter: Filter to apply on query.
        :param dict data: The columns and values to be updated.
        :return: List containing all updated records.
        :rtype: list
        :raises UpdateTableException: If a given column could not be found on database record.
        """
        updated_list = list()
        for register in cls.search(
            connection, filter=filter, after=-1, is_active="all"
        ):
            if hasattr(register, "updated_at"):
                setattr(register, "updated_at", datetime.utcnow())
            for column, value in data.items():
                try:
                    getattr(register, column)
                    setattr(register, column, value)
                except AttributeError:
                    raise UpdateTableException(
                        status=404,
                        error="Not Found",
                        message="Campo não encontrado",
                        error_details=[
                            ErrorDetails(
                                message=f"O campo {column} não existe"
                            ).to_dict()
                        ],
                    )
            updated_list.append(register)

        connection.commit()

        return updated_list

    def insert(self, connection: DatabaseService):
        """
        Insert record on database. The object should be a parent of DatabaseCrud class.

        :param connection: Database connection.
        :return: Self
        """
        connection.add(self)
        connection.commit()
        return self

    def delete(self, connection: DatabaseService):
        """
        Delete record on database. The object should be a parent of DatabaseCrud class.

        :param connection: Database connection.
        """
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
            # if type(attr_value) is datetime:
            #     attr_value = attr_value.strftime("%Y-%m-%d")
            elif type(attr_value) is Decimal:
                attr_value = float(attr_value)
            else:
                attr_value = str(attr_value)
            class_attr_dict[attr.name] = attr_value
        return class_attr_dict

    def to_dict(self, no_fk: bool = True, no_none: bool = True, no_id: bool = True):
        """
        Makes a dictionary out of an DataBaseCrud object instance.

        :param bool no_fk: Whether or not to include fk columns in final dict.
        :param bool no_none: Whether or not to include null columns in final dict.
        :param bool no_id: Whether or not to include id columns in final dict.
        """
        return self.__parse_table(no_fk, no_none, no_id)

    def __repr__(self):
        return f"{type(self).__qualname__}({self.to_dict()})"
