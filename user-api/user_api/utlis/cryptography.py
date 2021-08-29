from cryptography.fernet import Fernet


def generate_key() -> str:
    """
    Gera uma chave criptografica, do tipo string.
    """
    return Fernet.generate_key().decode()


def encrypt_message(message: str, key: str) -> str:
    """
    Encripta uma mensagem do tipo string, devolvendo o resultado em string.
    """
    f = Fernet(key.encode())
    return f.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt_message(encrypted_message: str, key: str) -> str:
    """
    Decripta uma mensagem criptografada, devolvendo uma string.
    """
    f = Fernet(key.encode())
    return f.decrypt(encrypted_message.encode("utf-8")).decode("utf-8")
