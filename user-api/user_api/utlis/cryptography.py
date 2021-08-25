from cryptography.fernet import Fernet


def generate_key():
    """
    Generates a key
    """
    return Fernet.generate_key().decode()


def encrypt_message(message: str, key: str):
    """
    Encrypts a message
    """
    f = Fernet(key.encode())
    return f.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt_message(encrypted_message: str, key: str):
    """
    Decrypts an encrypted message
    """
    f = Fernet(key.encode())
    return f.decrypt(encrypted_message.encode("utf-8")).decode("utf-8")
