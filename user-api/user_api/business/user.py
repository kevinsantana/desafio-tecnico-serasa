from sqlalchemy.exc import IntegrityError

from user_api.exceptions import ErrorDetails
from user_api.entities.user import User as user_entity
from user_api.exceptions.user import UserAlreadyInserted
from user_api.database.database_service import DatabaseService


def insert_user(user: user_entity):
    with DatabaseService() as conn:
        try:
            user.cpf = user.cpf.replace(".", "").replace("-", "")
            user.insert(conn)
            return user
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
