"""Encryption and decryption utilities for .env file values."""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_value(value: str, password: str) -> str:
    """Encrypt a single string value. Returns base64-encoded salt+ciphertext."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(value.encode())
    combined = salt + token
    return base64.urlsafe_b64encode(combined).decode()


def decrypt_value(encoded: str, password: str) -> str:
    """Decrypt a value produced by encrypt_value."""
    combined = base64.urlsafe_b64decode(encoded.encode())
    salt = combined[:SALT_SIZE]
    token = combined[SALT_SIZE:]
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token).decode()


def encrypt_env(env: dict, password: str) -> dict:
    """Return a new dict with all values encrypted."""
    return {k: encrypt_value(v, password) for k, v in env.items()}


def decrypt_env(env: dict, password: str) -> dict:
    """Return a new dict with all values decrypted."""
    return {k: decrypt_value(v, password) for k, v in env.items()}
