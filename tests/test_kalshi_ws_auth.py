from __future__ import annotations

import base64

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


def test_ws_auth_builds_rsa_pss_headers_from_private_key_path(tmp_path) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_path = tmp_path / "fake.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

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
