from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Sequence

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
    name = Column(String, nullable=False)
    cpf = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
