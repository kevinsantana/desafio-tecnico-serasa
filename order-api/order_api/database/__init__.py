import abc
from uuid import uuid4

import elasticsearch
from elasticsearch import Elasticsearch
from loguru import logger

from order_api.config import envs
from order_api.exceptions import ErrorDetails
from order_api.exceptions.order import (
    OrderAlreadyInsertedException,
    OrderNotFoundException,
    UpdateOrderException,
)


class Database:
    # TODO: try na conexao
    def __connect(self):
        self.__es = Elasticsearch([{"host": envs.DB_HOST, "port": envs.DB_PORT}])

    def __disconnect(self):
        self.__es.close()

    def create_index_if_not_exists(self, index: str):
        self.__connect()
        try:
            self.__es.indices.create(index=index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error == "resource_already_exists_exception":
                pass
            else:
                raise Exception(f"Falha na criacao do indice {ex}")
        self.__disconnect()

    def insert(
        self,
        document: dict,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ) -> str:
        self.__connect()
        try:
            response = self.__es.create(
                index=index, doc_type=doc_type, id=id, body=document
            )
        except elasticsearch.exceptions.NotFoundError:
            self.create_index_if_not_exists(index=index)
        except elasticsearch.exceptions.ConflictError:
            raise OrderAlreadyInsertedException(
                status=409,
                error="Conflict",
                message="Dado repetido",
                error_details=[
                    ErrorDetails(message=f"O id {id} do pedido é repetido").to_dict()
                ],
            )
        self.__disconnect()
        return response

    def list_one(
        self,
        id: int,
        index: str = "orders",
        doc_type: str = "order",
    ):
        self.__connect()
        try:
            response = self.__es.get(index=index, id=id, doc_type=doc_type)
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="Pedido não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"O pedido {id} não foi encontrado na base"
                    ).to_dict()
                ],
            )
        self.__disconnect()
        return response

    def update(
        self,
        doc: dict,
        id: int,
        index: str = "orders",
        doc_type: str = "order",
    ):
        self.__connect()
        try:
            response = self.__es.index(index=index, id=id, body=doc, doc_type=doc_type)
        except elasticsearch.exceptions.RequestError as error:
            logger.error(error)
            raise UpdateOrderException(
                status=400,
                error="Bad Request",
                message="Campo inválido",
                error_details=[ErrorDetails(message=f"O campo não existe").to_dict()],
            )
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="Pedido não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"O pedido {id} não foi encontrado na base"
                    ).to_dict()
                ],
            )
        self.__disconnect()
        return response

    def delete(
        self,
        id: int,
        index: str = "orders",
        doc_type: str = "order",
    ):
        self.__connect()
        try:
            response = self.__es.delete(index=index, id=id, doc_type=doc_type)
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="Pedido não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"O pedido {id} não foi encontrado na base"
                    ).to_dict()
                ],
            )
        self.__disconnect()
        return response

    def list_all(
        self,
        quantity: int = 10,
        page: int = 0,
        index: str = "orders",
        doc_type: str = "order",
    ):
        offset = (page - 1) * quantity
        document = {"query": {"match_all": {}}}
        self.__connect()
        response = self.__es.search(
            body=document, index=index, doc_type=doc_type, from_=offset, size=quantity
        )
        total = self.__es.count(body=document, index=index, doc_type=doc_type).get(
            "count"
        )
        return response.get("hits").get("hits"), total

    @abc.abstractclassmethod
    def dict(self):
        raise NotImplementedError
