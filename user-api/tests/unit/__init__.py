from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError


@dataclass
class UserMock:
    name: str = "Isabella Rebeca Agatha Alves"
    cpf: str = "030.077.400-10"
    email: str = "seuemail@mail.com.br"
    phone_number: str = "99999-9999"
    raise_integrity_error: bool = False

    def insert(self, conn):
        if self.raise_integrity_error:
            raise IntegrityError(statement="", params="", orig="")
        return self

    def to_dict(self, no_id=False, no_fk=False):
        return self.__dict__

    def update(self, conn, filter, data):
        return [UserMock()]
