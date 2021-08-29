from cryptography.fernet import Fernet

from user_api.exceptions import ErrorDetails
from user_api.exceptions.cryptography import EmptySecretKeyException


def generate_key() -> str:
    """
    Gera uma chave criptografica, do tipo string.
    """
    return Fernet.generate_key().decode()


def encrypt_message(message: str, key: str) -> str:
    """
    Encripta uma mensagem do tipo string, devolvendo o resultado em string.
    """
    try:
        f = Fernet(key.encode())
    except AttributeError:
        raise EmptySecretKeyException(
            status=404,
            error="Not Found",
            message="Senha de criptografia vazia",
            error_details=[
                ErrorDetails(message="A senha para criptografia dos dados não pode ser vazia").to_dict()
            ],
        )
    return f.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt_message(encrypted_message: str, key: str) -> str:
    """
    Decripta uma mensagem criptografada, devolvendo uma string.
    """
    f = Fernet(key.encode())
    return f.decrypt(encrypted_message.encode("utf-8")).decode("utf-8")
