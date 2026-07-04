from __future__ import annotations

import base64
import os

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from edmn_trader.adapters.kalshi.ws_auth import (
    KALSHI_WS_PATH,
    KalshiWsAuthBlocked,
    KalshiWsAuthConfig,
    build_kalshi_ws_headers,
    load_kalshi_ws_auth_config_from_env,
)


def test_ws_auth_missing_credentials_blocks() -> None:
    with pytest.raises(KalshiWsAuthBlocked) as exc:
        load_kalshi_ws_auth_config_from_env({})

    assert exc.value.code == "NO_WS_CREDENTIALS"


def test_ws_auth_rejects_key_inside_git_repo(tmp_path) -> None:
    key_path = _write_fake_key(tmp_path / "repo" / "fake.pem")
    (tmp_path / "repo" / ".git").mkdir()

    with pytest.raises(KalshiWsAuthBlocked) as exc:
        load_kalshi_ws_auth_config_from_env(
            {
                "KALSHI_DEMO_API_KEY_ID": "fake-key-id",
                "KALSHI_DEMO_PRIVATE_KEY_PATH": str(key_path),
            }
        )

    assert exc.value.code == "WS_CREDENTIAL_STORAGE_UNSAFE"


def test_ws_auth_builds_rsa_pss_headers_from_private_key_path(tmp_path) -> None:
    private_key, key_path = _fake_key(tmp_path / "fake.pem")

    headers = build_kalshi_ws_headers(
        KalshiWsAuthConfig(api_key_id="fake-key-id", private_key_path=key_path),
        timestamp_ms=123456789,
    )

    assert headers["KALSHI-ACCESS-KEY"] == "fake-key-id"
    assert headers["KALSHI-ACCESS-TIMESTAMP"] == "123456789"
    private_key.public_key().verify(
        base64.b64decode(headers["KALSHI-ACCESS-SIGNATURE"]),
        f"123456789GET{KALSHI_WS_PATH}".encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256(),
    )


def _fake_key(path):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, _write_key(path, private_key)


def _write_fake_key(path):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return _write_key(path, private_key)


def _write_key(path, private_key):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    os.chmod(path, 0o600)
    return path
