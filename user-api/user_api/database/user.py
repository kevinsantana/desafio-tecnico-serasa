from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, VARCHAR, CHAR, Sequence

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
    name = Column(VARCHAR(100), nullable=False)
    cpf = Column(CHAR(11), index=True, nullable=False, unique=True)
    email = Column(VARCHAR(55), nullable=True)
    phone_number = Column(VARCHAR(10), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
