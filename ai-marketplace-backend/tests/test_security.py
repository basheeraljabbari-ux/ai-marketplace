import uuid
import time

from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)


def test_password_hash_and_verify():
    hashed = hash_password("MySecurePass123")
    assert hashed != "MySecurePass123"
    assert verify_password("MySecurePass123", hashed)
    assert not verify_password("WrongPassword", hashed)


def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "user")
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "user"
    assert payload["type"] == "access"


def test_refresh_token_has_different_type_than_access():
    user_id = uuid.uuid4()
    refresh = create_refresh_token(user_id)
    payload = decode_token(refresh)

    assert payload["type"] == "refresh"
    assert "role" not in payload  # refresh token ما يحمل role عمداً — أخف صلاحيات


def test_decode_invalid_token_returns_none():
    assert decode_token("this.is.not.a.valid.jwt") is None


def test_decode_tampered_token_returns_none():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "user")
    tampered = token[:-5] + "aaaaa"
    assert decode_token(tampered) is None
