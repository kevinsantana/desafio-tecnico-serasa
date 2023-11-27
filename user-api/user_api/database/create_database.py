from loguru import logger
from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError

from user_api.database.database_service import Base, engine

from .user import *  #  noqa


def create_database(reset: bool):
    """
    Create the database.

    :param bool reset: Either or not the database should be dropped before is
    created.
    """
    try:
        if reset:
            logger.debug("Dropping database")
            Base.metadata.drop_all(engine)

        logger.debug("Creating database")
        Base.metadata.create_all(engine)

    except (IntegrityError, InvalidRequestError, OperationalError) as error:
        logger.error(f"Error on database creation: {error}")
