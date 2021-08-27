import abc
from uuid import uuid4

from elasticsearch import Elasticsearch

from order_api.config import envs


class Database:
    # TODO: try na conexao
    def __connect(self):
        self.__connection = Elasticsearch([envs.DB_URL])

    def __disconnect(self):
        self.__connection.close()

    # TODO: try na insercao
    # TODO: insercao documento repetido
    # TODO: atualizar documento vazio
    def insert(
        self,
        document: dict,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ) -> str:
        """
        Insere um documento em uma collection.

        :param collection: Nome da collection onde o documento será inserido
        :type collection: str
        :param document: Documento a ser inserido
        :type document: dict
        :return: id gerado
        :rtype: str
        """
        result = None
        self.__connect()
        response = self.__connection.index(
            index=index, doc_type=doc_type, id=id, body=document
        )
        if response.get("result") == "updated":
            result = response.get("_version")
        else:
            result = response.get("_id")
        self.__disconnect()
        return result

    @abc.abstractclassmethod
    def dict(self):
        raise NotImplementedError
