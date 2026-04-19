"""Tests for envoy_cli.crypto encryption utilities."""

import pytest
from envoy_cli.crypto import (
    encrypt_value,
    decrypt_value,
    encrypt_env,
    decrypt_env,
    derive_key,
)

PASSWORD = "s3cr3t-p@ssword"


def test_encrypt_decrypt_roundtrip():
    original = "super_secret_value"
    encrypted = encrypt_value(original, PASSWORD)
    assert encrypted != original
    assert decrypt_value(encrypted, PASSWORD) == original


def test_encrypt_produces_different_ciphertexts():
    """Same value encrypted twice should differ (random salt)."""
    v1 = encrypt_value("hello", PASSWORD)
    v2 = encrypt_value("hello", PASSWORD)
    assert v1 != v2


def test_decrypt_wrong_password_raises():
    encrypted = encrypt_value("value", PASSWORD)
    with pytest.raises(Exception):
        decrypt_value(encrypted, "wrongpassword")


def test_encrypt_env_roundtrip():
    env = {"DB_HOST": "localhost", "API_KEY": "abc123", "DEBUG": "true"}
    encrypted = encrypt_env(env, PASSWORD)
    assert all(v != env[k] for k, v in encrypted.items())
    decrypted = decrypt_env(encrypted, PASSWORD)
    assert decrypted == env


def test_encrypt_empty_string():
    assert decrypt_value(encrypt_value("", PASSWORD), PASSWORD) == ""


def test_derive_key_deterministic():
    salt = b"fixedsalt1234567"
    k1 = derive_key(PASSWORD, salt)
    k2 = derive_key(PASSWORD, salt)
    assert k1 == k2


def test_derive_key_different_salts():
    import os
    k1 = derive_key(PASSWORD, os.urandom(16))
    k2 = derive_key(PASSWORD, os.urandom(16))
    assert k1 != k2
