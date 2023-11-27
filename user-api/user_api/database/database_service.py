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
    An api for interacting with sqlalchemy. When creating the object, it associates this instance
    to a sqlalchemy session. When the object is deleted by the `garbage collector`
    the session is terminated, collecting an exception if this happens.
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
    Basic database operations (CRUD). The methods are of the class, because interaction
    with the sqlalchemy session is done from a class that represents a table in
    the database. a table in the database, thus abstracting a layer of complexity
    for the developer.
    """

    @classmethod
    def list_one(
        cls,
        connection: DatabaseService,
        filter: tuple = None,
        order_by: tuple = None,
    ):
        """
        Finds and returns the first record in the database from the filter
        entered.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filter to apply on query.
        :param tuple order_by: Whether to apply an order_by of type
            (column, sort).
        :return: Record found.
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
        Returns all the records in the database from the filter entered.
        Paging the result and returning a generator.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        :param int page: Offset of the query.
        :param int quantity: Number of records per page
        :param is_active: If only active records and records from tables that have an
            is_active' column.
        :type is_active: bool, optional
        :return: Result of the query.
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
        Searches for all records from the filter entered. Paginating the result
        and returning a generator.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filter to be applied to the query, of type (Table.column == column).
        :param int after: Number of results that should be skipped in the query.
        :param int limit: Limit of results per page
        :param is_active: If only active records and records from tables that have an
            is_active' column.
        :type is_active: bool, optional
        :param tuple order_by: Whether an order_by of type (column, sort).
        :return: Result of the query.
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
        Updates a database record.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filter to be applied to the query, of type (Table.column == column)
        :param dict data: Column and values to be updated of type column: value.
        :raises UpdateTableException: If any of the columns in the data parameter
            parameter does not exist in the table.
        :return: List of all records updated from the filter entered.
        :rtype: list
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
                        message="Field not found",
                        error_details=[
                            ErrorDetails(
                                message=f"The field {column} does not exist"
                            ).to_dict()
                        ],
                    )
            updated_list.append(register)

        connection.commit()

        return updated_list

    def insert(self, connection: DatabaseService):
        """
        Adds a record to the database.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        :return: Self
        """
        connection.add(self)
        connection.commit()
        return self

    def delete(self, connection: DatabaseService):
        """
        Deletes a record in the database.

        :param connection: Connection to the database, of type :class:`database.database_service.DatabaseServicer`.
        """
        connection.remove(self)
        connection.commit()

    def __parse_table(
        self, no_fk: bool = True, no_none: bool = True, no_id: bool = True
    ) -> dict:
        """
        Helper method for formatting an advent table from the database.

        :param no_fk: If the dictionary contains foreign key columns
            should be added to the final formatting.
        :type no_fK: bool, optional
        :param no_none: Whether null columns should be added to the final formatting.
        :type no_none: bool, optional
        :param no_id: Whether or not columns of type primary key should be added to
            to the final formatting.
        :type no_id: bool, optional
        """
        class_attr_dict = dict()
        for attr in self.__table__.columns:
            if no_fk and attr.name.startswith("fk"):
                continue
            if no_id and attr.name.startswith("id"):
                continue
            attr_value = getattr(self, attr.name)
            if no_none and attr_value is None:
                continue
            elif type(attr_value) is Decimal:
                attr_value = float(attr_value)
            else:
                attr_value = str(attr_value)
            class_attr_dict[attr.name] = attr_value
        return class_attr_dict

    def to_dict(self, no_fk: bool = True, no_none: bool = True, no_id: bool = True):
        """
        Returns a dictionary from an instance of the class :class:`database.database_service.DatabaseCrud`

        :param bool no_fk: Whether or not data of type foreign key should be added
            to the dictionary.
        :type no_fk: bool, optional
        :param bool no_none: Whether or not null columns should be added to the dictionary.
        :type no_none: bool, optional
        :param bool no_id: Whether or not primary key data should be added to the dictionary.
            to the dictionary.
        :type no_id: bool, optional
        """
        return self.__parse_table(no_fk, no_none, no_id)

    def __repr__(self):
        return f"{type(self).__qualname__}({self.to_dict()})"
