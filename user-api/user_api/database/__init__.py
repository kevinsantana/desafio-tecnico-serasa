# from loguru import logger
# from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError

# from user_api.database.database_service import Base, engine

# from .user import *  #  noqa


# def create_database(reset: bool):
#     try:
#         if reset:
#             logger.debug("Resetando banco de dados")
#             Base.metadata.drop_all(engine)

#         logger.debug("Criando banco de dados")
#         Base.metadata.create_all(engine)

#     except (IntegrityError, InvalidRequestError, OperationalError) as error:
#         logger.debug(f"Erro na criação ou reset do banco de dados: {error}")
