from dataclasses import dataclass

from user_api.config import envs
from user_api.database.user import User as UserDB
from user_api.utlis.cryptography import encrypt_message, decrypt_message


@dataclass()
class User(UserDB):
    """
    Following the principles of clean architecture, this class would be an adapter.
    Keeping the business logic separate from the database.
    """

    def encrypt(self):
        """
        Encrypt the sensitive attributes of the User class, using python.cryptography.
        The attributes must be strings.
        """
        self.email = encrypt_message(self.email, envs.SECRET_KEY)
        self.cpf = encrypt_message(self.cpf, envs.SECRET_KEY)
        self.phone_number = encrypt_message(self.phone_number, envs.SECRET_KEY)

    def decrypt(self):
        """
        Decrypts the user's sensitive attributes.
        """
        self.email = decrypt_message(self.email, envs.SECRET_KEY)
        self.cpf = decrypt_message(self.cpf, envs.SECRET_KEY)
        self.phone_number = decrypt_message(self.phone_number, envs.SECRET_KEY)
        return self

    def to_object(self):  # pragma: no cover
        """
        Returns an object of type :class:`entities.user.User` from a record
        from the database.
        """
        return User(**self.to_dict())

    def __repr__(self) -> str:
        return f"{self.to_dict()}"
