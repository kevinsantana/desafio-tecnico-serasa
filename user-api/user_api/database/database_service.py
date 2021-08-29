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
    Um api para interação com sqlalchemy. Ao criar o objeto, associa esta instância
    a uma sessão do sqlalchemy. Quando o objeto é deletado pelo `garbage collector`
    a sessão é encerrada, coletando uma exceção caso aconteça.
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
    Operaçãoes básicas de banco de dados (CRUD). Os métodos são da classe, pois,
    a interação com a sessão do sqlalchemy é feita a partir de uma classe que representa
    uma tabela no banco de dados, assim, abstraindo para o desenvolvedor uma camada
    de complexidade.
    """

    @classmethod
    def list_one(
        cls,
        connection: DatabaseService,
        filter: tuple = None,
        order_by: tuple = None,
    ):
        """
        Encontra e retorna o primeiro registro no banco de dados a partir do filtro
        informado.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filter to apply on query.
        :param tuple order_by: Se o resultado deve ser aplicado um order_by do tipo
        (coluna, ordenacao).
        :return: Registro encontrado.
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
        Retorna todos os registros do banco de dados a partir do filtro informado.
        Paginando o resultado e retornando um generator.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        :param int page: Offset da query.
        :param int quantity: Quantidade de registros por página
        :param is_active: Se apenas registros ativos e de tabelas que possuam uma
        coluna 'is_active'.
        :type is_active, bool, optional
        :return: Resultado da consulta.
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
        Procura todos os registros a partir do filtro informado. Paginando o resultado
        e devolvendo um generator.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filtro a ser aplicado na consulta, do tipo (Tabela.coluna == coluna).
        :param int after: Quantidade de resultados que devem ser pulados na consulta.
        :param int limit: Limite de resultados por página
        :param is_active: Se apenas registros ativos e de tabelas que possuam uma
        coluna 'is_active'.
        :type is_active: bool, optional
        :param tuple order_by: Se o resultado deve ser aplicado um order_by do tipo
        (coluna, ordenacao).
        :return: Resultado da consulta.
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
        Atualiza um registro do banco de dados.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        :param tuple filter: Filtro a ser aplicado na consulta, do tipo (Tabela.coluna == coluna)
        :param dict data: Coluna e valores a serem atualizados do tipo coluna: valor.
        :raises UpdateTableException: Se alguma coluna informada no parâmetro data
        não existirem na tabela.
        :return: Lista com todos os registros atualizados a partir do filtro informado.
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
        Insere um registro no banco de dados.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        :return: Self
        """
        connection.add(self)
        connection.commit()
        return self

    def delete(self, connection: DatabaseService):
        """
        Deleta um registro no banco de dados.

        :param connection: Conexão com o banco de dados, do tipo :class:`database.database_service.DatabaseServicer`.
        """
        connection.remove(self)
        connection.commit()

    def __parse_table(
        self, no_fk: bool = True, no_none: bool = True, no_id: bool = True
    ) -> dict:
        """
        Método auxiliar para formatar uma tabela adventa do banco de dados.

        :param no_fk: Se no dicionário construídos colunas do tipo foreign key
        devem ser adicionadas a formatação final.
        :type no_fK: bool, optional
        :param no_none: Se colunas nulas devem ser adicionadas a formatação final.
        :type no_none: bool, optional
        :param no_id: Se colunas do tipo primary key devem ou não ser adicionadas
        a formatação final.
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
        Retorna um dicionário a partir de uma instância da classe :class:`database.database_service.DatabaseCrud`

        :param bool no_fk: Se dados do tipo foreign key devem ou não ser adicionados
        ao dicionário.
        :type no_fk: bool, optional
        :param bool no_none: Se colunas nulas devem ou não ser adicionados ao dicionário.
        :type no_none: bool, optional
        :param bool no_id: Se dados do tipo primary key devem ou não ser adicionados
        ao dicionário.
        :type no_id: bool, optional
        """
        return self.__parse_table(no_fk, no_none, no_id)

    def __repr__(self):
        return f"{type(self).__qualname__}({self.to_dict()})"
