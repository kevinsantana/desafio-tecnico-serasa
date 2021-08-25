from dataclasses import dataclass

from user_api.config import envs
from user_api.database.user import User as UserDB
from user_api.utlis.cryptography import encrypt_message, decrypt_message


@dataclass()
class User(UserDB):

    def encrypt(self):
        self.email = encrypt_message(self.email, envs.SECRET_KEY)
        self.cpf = encrypt_message(self.cpf, envs.SECRET_KEY)
        self.phone_number = encrypt_message(self.phone_number, envs.SECRET_KEY)

    def decrypt(self):
        self.email = decrypt_message(self.email, envs.SECRET_KEY)
        self.cpf = decrypt_message(self.cpf, envs.SECRET_KEY)
        self.phone_number = decrypt_message(self.phone_number, envs.SECRET_KEY)
        return self

    def to_object(self):  # pragma: no cover
        return User(**self.to_dict())

    def __repr__(self) -> str:
        return f"{self.to_dict()}"
