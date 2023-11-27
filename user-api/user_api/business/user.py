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
    Inserts a user into the database, encrypting sensitive data. Sanitizes
    the cpf and phone data, removing non-numeric characters.

    :param user_entity user: Instance of the class :class:`entities.user.User`.
    :raises UserAlreadyInserted: The cpf number entered already exists in the database.
    :return: Id of the user inserted into the database.
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
                message="Repeated data",
                error_details=[
                    ErrorDetails(
                        message=f"The field {user.to_dict(no_fk=False)} is repeated"
                    ).to_dict()
                ],
            )


def update_user(id_user: int, update_data: dict) -> bool:
    """
    Updates a user.

    :param int id_user: Id of the user to be updated.
    :param dict update_data: Dictionary in column format: value of the data that
        to be updated.
    :raises UpdateUserException: The user was not found in the database.
    :return: True if the user was successfully updated.
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
                message="User not found",
                error_details=[
                    ErrorDetails(message=f"Failed to update user: {id_user}").to_dict()
                ],
            )


def delete_user(id_user: int) -> bool:
    """
    Deletes a user.

    :param int id_user: User to be deleted.
    :raises DeleteUserException: The user entered cannot be found.
    :return: True if the user is successfully deleted.
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
                message="User not found",
                error_details=[
                    ErrorDetails(message=f"Failed to delete user: {id_user}").to_dict()
                ],
            )


def list_one(id_user: int) -> user_entity:
    """
    Returns the user from their id. Decrypting the data retrieved
    from the database.

    :param int id_user: User id.
    :raises GetUserException: The user entered was not found.
    :return: Instance of class :class:`entities.user.User`.
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
    Lists all users in the database, paginating the result. Decrypting the
    retrieved data in the database.

    :param int quantity: Number of users per page.
    :param int page: Result page.
    :return: List of all users found in the database.
    :rtype: list
    """
    with DatabaseService() as conn:
        users = [
            user.decrypt().to_dict()
            for user in user_entity.find_all(conn, page=page, quantity=quantity)
        ]
        return users, len(users)
