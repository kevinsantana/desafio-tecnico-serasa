from datetime import datetime

from sqlalchemy import Column, Integer, Date, VARCHAR, CHAR, Sequence

from user_api.database.database_service import Base, DataBaseCrud


class User(Base, DataBaseCrud):

    __tablename__ = "USER"

    id_user = Column(
        Integer,
        Sequence("id_user_sequence", metadata=Base.metadata),
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    name = Column(VARCHAR(100), nullable=True)
    cpf = Column(CHAR(11), index=True, nullable=True)
    email = Column(VARCHAR(55), nullable=True)
    phone_number = Column(VARCHAR(10), nullable=False)
    created_at = Column(Date, nullable=False, default=datetime.now())
    updated_at = Column(Date, nullable=True, default=datetime.now())
