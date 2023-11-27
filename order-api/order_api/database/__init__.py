import abc
from uuid import uuid4

import elasticsearch
from loguru import logger
from elasticsearch import Elasticsearch

from order_api.config import envs

from order_api.exceptions import ErrorDetails
from order_api.exceptions.order import (
    OrderAlreadyInsertedException,
    OrderNotFoundException,
    UpdateOrderException,
)
from order_api.exceptions.database import QueryMalformedException


class Database:
    """
    Each database table is a class, where each column is an attribute
    of the class and the methods are its transactions (DML or DDL). The data returned
    of database operations are dictionaries in which each key is the column
    of the table and the value of this key is the result of the operation, for this, all
    Classes that inherit from DataBase need to implement its dict method.
    Thus, it is possible to instantiate an object of the class, that is, a database table
    of data mapping each attribute of the class to a column of this table. And still,
    Taking advantage of OO, it is not necessary for other classes to implement transactions
    common to all database tables: insert, list_one, list_all, etc.
    """

    def __connect(self):
        """
        Connects to the database, the connection data is captured
        of environment variables exported in the order-api/order_api/config.py file.
        Creates the __es attribute of the :class:`Elasticsearch` class to manipulate elasticsearch.
        :raises ConnectionError: If connection to the database is not possible.
        """
        try:
            self.__es = Elasticsearch([{"host": envs.DB_HOST, "port": envs.DB_PORT}])
        except elasticsearch.exceptions.ConnectionError as error:
            logger.error(
                f"Failed to connect to database: {envs.DB_HOST} {envs.DB_PORT}: {error}"
            )

    def __disconnect(self):
        """
        Closes the connection to the database.
        """
        self.__es.close()

    def create_index_if_not_exists(self, index: str):
        """
        Creates a new index, if it does not exist, ignoring the existence of the same one
        index with the given name.
        :param str index: Name of the index that will be created.
        """
        self.__connect()
        try:
            self.__es.indices.create(index=index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error == "resource_already_exists_exception":
                pass
            else:
                logger.error(f"Failed to create index {index}: {ex}")
        self.__disconnect()

    def insert(
        self,
        document: dict,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Inserts a new document into elasticsearch.

        :param dict document: Instance of the document type with the data that will be
            included, in dict format.
        :param id: Id of the new document, uuid if not provided.
        :type id: str, optional
        :param index: Index at which the document will be inserted, by default in the index
            'orders'.
        :type index: str, optional
        :param doc_type: Document type of the inserted document, by default 'order'.
        :type doc_type: str, optional
        :raises OrderAlreadyInsertedException: If the id entered already exists in the base.
        :return: Insertion response.
        :rtype: dict
        """
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
                message="Repeated data",
                error_details=[
                    ErrorDetails(message=f"Order id {id} is repeated").to_dict()
                ],
            )
        self.__disconnect()
        return response

    def list_one(
        self,
        id: str,
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Lists a request from the database, based on its id.

        :param str id: Order id.
        :param index: Index at which the document will be inserted, by default in the index
            'orders'.
        :type index: str, optional
        :param doc_type: Document type of the inserted document, by default 'order'.
        :type doc_type: str, optional
        :raises OrderNotFoundException: The order was not found.
        :return: Search response.
        :rtype: dict
        """
        self.__connect()
        try:
            response = self.__es.get(index=index, id=id, doc_type=doc_type)
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="Order not found",
                error_details=[
                    ErrorDetails(message=f"Order {id} was not found").to_dict()
                ],
            )
        self.__disconnect()
        return response

    def update(
        self,
        doc: dict,
        id: str,
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Updates an order.

        :param dict doc: Dictionary with the fields and values to be updated.
        :param str id: Id of the order to be updated.
        :param index: Index at which the document will be inserted, by default in the index
            'orders'.
        :type index: str, optional
        :param doc_type: Document type of the inserted document, by default 'order'.
        :type doc_type: str, optional
        :raises UpdateOrderException: When a field that does not exist in the order is
            informed.
        :raises OrderNotFoundException: The order was not found.
        :return: Update response.
        :rtype: dict
        """
        self.__connect()
        try:
            response = self.__es.index(index=index, id=id, body=doc, doc_type=doc_type)
        except elasticsearch.exceptions.RequestError as error:
            logger.error(error)
            raise UpdateOrderException(
                status=400,
                error="Bad Request",
                message="Invalid field",
                error_details=[ErrorDetails(message="Field does not exist").to_dict()],
            )
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="Order not found",
                error_details=[
                    ErrorDetails(message=f"order {id} was not found").to_dict()
                ],
            )
        self.__disconnect()
        return response

    def delete(
        self,
        id: int,
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Deletes a request from the database.

        :param str id: Id of the order to be updated.
        :param index: Index at which the document will be inserted, by default in the index
            'orders'.
        :type index: str, optional
        :param doc_type: Document type of the inserted document, by default 'order'.
        :type doc_type: str, optional
        :raises OrderNotFoundException: The order was not found.
        :return: Update response.
        :rtype: dict
        """
        self.__connect()
        try:
            response = self.__es.delete(index=index, id=id, doc_type=doc_type)
        except elasticsearch.exceptions.NotFoundError:
            raise OrderNotFoundException(
                status=404,
                error="Not Found",
                message="order not found",
                error_details=[
                    ErrorDetails(message=f"order {id} was not found").to_dict()
                ],
            )
        self.__disconnect()
        return response

    def list_all(
        self,
        query: dict = None,
        quantity: int = 10,
        page: int = 0,
        index: str = "orders",
        doc_type: str = "order",
    ) -> tuple:
        """
        List all base requests.

        .. note::
            This method does not work when the database has more than 10,000 records.
            Pagination is done using the `from` with `size` parameters from the python api
            from elasticsearch.
            `Stackoverflow <https://stackoverflow.com/a/59142866>`_

        :param query: Search parameters to filter the result, in the accepted format
            via the elasticsearch api.
        :type query: dict, optional
        :param int quantity: Number of records per page.
        :param int page: Return page.
        :param index: Index at which the document will be inserted, by default in the index 'orders'.
        :type index: str, optional
        :param doc_type: Document type of the inserted document, by default 'order'.
        :type doc_type: str, optional
        :raises QueryMalformedException: If the query format is invalid.
        :return: Base documents and total records.
        :rtype: tuple
        """
        if query:
            document = {"query": {"match": query}}
        else:
            document = {"query": {"match_all": {}}}
        logger.debug(query)
        logger.debug(document)
        offset = (page - 1) * quantity
        self.__connect()
        try:
            response = self.__es.search(
                body=document,
                index=index,
                doc_type=doc_type,
                from_=offset,
                size=quantity,
            )
        except elasticsearch.exceptions.RequestError:
            raise QueryMalformedException(
                status=400,
                error="Bad request",
                message="Malformed query",
                error_details=[
                    ErrorDetails(message=f"Query {query} is malformed").to_dict()
                ],
            )
        total = self.__es.count(body=document, index=index, doc_type=doc_type).get(
            "count"
        )
        return response.get("hits").get("hits"), total

    @abc.abstractclassmethod
    def dict(self):
        raise NotImplementedError
