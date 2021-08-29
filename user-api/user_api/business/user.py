from sqlalchemy.exc import IntegrityError

from user_api.exceptions import ErrorDetails
from user_api.exceptions.user import (
    UserAlreadyInserted,
    UpdateUserException,
    DeleteUserException,
    GetUserException,
)

from user_api.config import envs
from user_api.entities.user import User as user_entity
from user_api.utlis.cryptography import encrypt_message
from user_api.database.database_service import DatabaseService


def insert_user(user: user_entity) -> int:
    """
    Insere um usuário no banco de dados, criptografando dados sensíveis. Sanitiza
    os dados de cpf e telefone, retirando caracteres não númericos.

    :param user_entity user: Instância da classe :class:`entities.user.User`.
    :raises UserAlreadyInserted: O número de cpf informado já existe na base.
    :return: Id do usuário inserido no banco de dados.
    :rtype: int
    """
    with DatabaseService() as conn:
        try:
            user.cpf = user.cpf.replace(".", "").replace("-", "")
            user.phone_number = user.phone_number.replace("-", "")
            user.encrypt()
            return user.insert(conn).decrypt().to_dict(no_id=False).get("id_user")
        except IntegrityError:
            raise UserAlreadyInserted(
                status=409,
                error="Conflict",
                message="Dado repetido",
                error_details=[
                    ErrorDetails(
                        message=f"O campo {user.to_dict(no_fk=False)} é repetido"
                    ).to_dict()
                ],
            )


def update_user(id_user: int, update_data: dict) -> bool:
    """
    Atualiza um usuário.

    :param int id_user: Id do usuário a ser atualizado.
    :param dict update_data: Dicionário no formato coluna: valor dos dados que
    serão atualizados.
    :raises UpdateUserException: O usuário não foi encontrado na base dados.
    :return: True se o usuário for atualizado com sucesso.
    :rtype: bool
    """
    with DatabaseService() as conn:
        if update_data.get("cpf"):
            update_data["cpf"] = encrypt_message(
                update_data.get("cpf").replace(".", "").replace("-", ""),
                envs.SECRET_KEY,
            )
        if update_data.get("phone_number"):
            update_data["phone_number"] = encrypt_message(
                update_data.get("phone_number").replace("-", ""), envs.SECRET_KEY
            )
        if update_data.get("email"):
            update_data["email"] = encrypt_message(
                update_data.get("email").replace("-", ""), envs.SECRET_KEY
            )

        database_filter = (user_entity.id_user == id_user,)
        updated_list = user_entity.update(
            conn, filter=database_filter, data=update_data
        )
        if len(updated_list) == 1:
            return True
        else:
            raise UpdateUserException(
                status=404,
                error="Not Found",
                message="Usuário não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"Erro ao atualizar usuário {id_user}"
                    ).to_dict()
                ],
            )


def delete_user(id_user: int) -> bool:
    """
    Deleta um usuário.

    :param int id_user: Usuário a ser deletado.
    :raises DeleteUserException: O usuário informado não pode ser encontrado.
    :return: True se o usuário for deletado com sucesso.
    :rtype: bool
    """
    with DatabaseService() as conn:
        database_filter = (user_entity.id_user == id_user,)
        user = user_entity.list_one(conn, database_filter)
        if user:
            user.delete(conn)
            return True
        else:
            raise DeleteUserException(
                status=404,
                error="Not Found",
                message="Usuário não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"Erro ao deletar o usuário {id_user}"
                    ).to_dict()
                ],
            )


def list_one(id_user: int) -> user_entity:
    """
    Retorna o usuário a partir do seu id. Descriptografando os dados recuperados
    do banco de dados.

    :param int id_user: Id do usuário.
    :raises GetUserException: O usuário informado não foi encontrado.
    :return: Instância da classe :class:`entities.user.User`.
    :rtype: :class:`entities.user.User`.
    """
    with DatabaseService() as conn:
        database_filter = (user_entity.id_user == id_user,)
        user = user_entity.list_one(conn, database_filter)
        if user:
            return user.decrypt().to_dict(no_none=True, no_id=False)
        else:
            raise GetUserException(
                status=404,
                error="Not Found",
                message="Usuário não encontrado",
                error_details=[
                    ErrorDetails(
                        message=f"O usuário {id_user} não foi encontrado"
                    ).to_dict()
                ],
            )


def list_all(quantity: int, page: int) -> list:
    """
    Lista todos os usuários da base, paginando o resultado. Descriptografando os
    dados recuperados no banco de dados.

    :param int quantity: Quantidade de usuários por página.
    :param int page: Página do resultado.
    :return: Lista com todos os usuários encontrados no banco de dados.
    :rtype: list
    """
    with DatabaseService() as conn:
        users = [
            user.decrypt().to_dict()
            for user in user_entity.find_all(conn, page=page, quantity=quantity)
        ]
        return users, len(users)
