from cryptography.fernet import Fernet

from user_api.exceptions import ErrorDetails
from user_api.exceptions.cryptography import EmptySecretKeyException


def generate_key() -> str:
    """
    Generates a cryptographic key of string type.
    """
    return Fernet.generate_key().decode()


def encrypt_message(message: str, key: str) -> str:
    """
    Encrypts a message of type string, returning the result as a string.
    """
    try:
        f = Fernet(key.encode())
    except AttributeError:
        raise EmptySecretKeyException(
            status=404,
            error="Not Found",
            message="Empty password",
            error_details=[
                ErrorDetails(
                    message="The password for data encryption must not be empty"
                ).to_dict()
            ],
        )
    return f.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt_message(encrypted_message: str, key: str) -> str:
    """
    Decrypts an encrypted message, returning a string.
    """
    f = Fernet(key.encode())
    return f.decrypt(encrypted_message.encode("utf-8")).decode("utf-8")
