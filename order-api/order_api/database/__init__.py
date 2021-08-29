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
    Cada tabela do banco de dados é uma classe, em que cada coluna é um atributo
    da classe e os métodos são suas transações (DML ou DDL). Os dados devolvidos
    de operações com o banco de dados são dicionários em que cada chave é a coluna
    da tabela e o valor desta chave é o resultado da operação, para isto, todas
    as classes que herdam de DataBase precisam implementar o seu método dict.
    Assim, é possível instanciar um objeto da classe, ou seja, uma tabela do banco
    de dados mapeando cada atributo da classe a uma coluna desta tabela. E, ainda,
    aproveitando da OO não é necessário que as demais classes implemetem as transações
    comuns a todas as tabelas do banco de dados: insert, list_one, list_all etc.
    """

    def __connect(self):
        """
        Efetua a conexão com o banco de dados, os dados de conexão são capturados
        de variáveis de ambientes exportadas no arquivo order-api/order_api/config.py.
        Cria o atributo __es da classe :class:`Elasticsearch` para manipular o elasticsearch.
        :raises ConnectionError: Se não for possível a conexão com o banco de dados.
        """
        try:
            self.__es = Elasticsearch([{"host": envs.DB_HOST, "port": envs.DB_PORT}])
        except elasticsearch.exceptions.ConnectionError as error:
            logger.error(
                f"Falha na conexão com o banco de dados {envs.DB_HOST} {envs.DB_PORT}: {error}"
            )

    def __disconnect(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.__es.close()

    def create_index_if_not_exists(self, index: str):
        """
        Cria um novo índice, caso não exista, ignorando a existência de um mesmo
        índice com o nome informado.
        :param str index: Nome do índice que será criado.
        """
        self.__connect()
        try:
            self.__es.indices.create(index=index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error == "resource_already_exists_exception":
                pass
            else:
                logger.error(f"Falha na criação do índice {index}: {ex}")
        self.__disconnect()

    def insert(
        self,
        document: dict,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Insere um novo documento no elasticsearch.

        :param dict document: Instância do document type com os dados que serão
        incluídos, no formato dict.
        :param id: Id do novo documento, uuid caso não seja informado.
        :type id: str, optional
        :param index: Indice no qual o documento será inserido, por padrão no índice
        'orders'.
        :type index: str, optional
        :param doc_type: Document type do documento inserido, por padrão 'order'.
        :type doc_type: str, optional
        :raises OrderAlreadyInsertedException: Caso o id informado já exista na base.
        :return: Response da inserção.
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
                message="Dado repetido",
                error_details=[
                    ErrorDetails(message=f"O id {id} do pedido é repetido").to_dict()
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
        Lista um pedido da base de dados, a partir do seu id.

        :param str id: Id do pedido.
        :param index: Indice no qual o documento será inserido, por padrão no índice
        'orders'.
        :type index: str, optional
        :param doc_type: Document type do documento inserido, por padrão 'order'.
        :type doc_type: str, optional
        :raises OrderNotFoundException: O pedido não foi encontrado.
        :return: Response da busca.
        :rtype: dict
        """
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
        id: str,
        index: str = "orders",
        doc_type: str = "order",
    ) -> dict:
        """
        Atualiza um pedido.

        :param dict doc: Dicionário com os campos e valores a serem atualizados.
        :param str id: Id do pedido a ser atualizado.
        :param index: Indice no qual o documento será inserido, por padrão no índice
        'orders'.
        :type index: str, optional
        :param doc_type: Document type do documento inserido, por padrão 'order'.
        :type doc_type: str, optional
        :raises UpdateOrderException: Quando um campo que não existe no pedido é
        informado.
        :raises OrderNotFoundException: O pedido não foi encontrado.
        :return: Response da atualização.
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
                message="Campo inválido",
                error_details=[ErrorDetails(message="O campo não existe").to_dict()],
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
    ) -> dict:
        """
        Deleta um pedido da base de dados.

        :param str id: Id do pedido a ser atualizado.
        :param index: Indice no qual o documento será inserido, por padrão no índice
        'orders'.
        :type index: str, optional
        :param doc_type: Document type do documento inserido, por padrão 'order'.
        :type doc_type: str, optional
        :raises OrderNotFoundException: O pedido não foi encontrado.
        :return: Response da atualização.
        :rtype: dict
        """
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
        query: dict = None,
        quantity: int = 10,
        page: int = 0,
        index: str = "orders",
        doc_type: str = "order",
    ) -> tuple:
        """
        Lista todos os pedidos da base.

        .. note::
            Este método não funciona quando a base tem mais de 10.000 registros.
            A paginação é feita usando os parâmetro `from` com `size` da api python
            do elasticsearch.
            `Stackoverflow <https://stackoverflow.com/a/59142866>`_

        :param query: Parâmetros da busca para filtrar o resultado, no formato aceito
        pela api do elasticsearch.
        :type query: dict, optional
        :param int quantity: Quantidade de registros por página.
        :param int page: Página do retorno.
        :param index: Indice no qual o documento será inserido, por padrão no índice
        'orders'.
        :type index: str, optional
        :param doc_type: Document type do documento inserido, por padrão 'order'.
        :type doc_type: str, optional
        :raises QueryMalformedException; Se o formato da query for inválido.
        :return: Documentos da base e total de registros.
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
                message="Query incorreta",
                error_details=[
                    ErrorDetails(
                        message=f"A query {query} está mal construída"
                    ).to_dict()
                ],
            )
        total = self.__es.count(body=document, index=index, doc_type=doc_type).get(
            "count"
        )
        return response.get("hits").get("hits"), total

    @abc.abstractclassmethod
    def dict(self):
        raise NotImplementedError
