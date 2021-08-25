from loguru import logger
from sqlalchemy.exc import IntegrityError

from user_api.exceptions import ErrorDetails
from user_api.exceptions.user import (
    UserAlreadyInserted,
    UpdateUserException,
    DeleteUserException,
    GetUserException,
)

from user_api.entities.user import User as user_entity
from user_api.database.database_service import DatabaseService


def insert_user(user: user_entity) -> int:
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


def update_user(id_user: int, update_data: dict):
    with DatabaseService() as conn:
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


def delete_user(id_user: int):
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


def list_one(id_user: int):
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


def list_all(quantity: int, page: int):
    with DatabaseService() as conn:
        users = [
            user.decrypt().to_dict()
            for user in user_entity.find_all(conn, page=page, quantity=quantity)
        ]
        return users, len(users)
