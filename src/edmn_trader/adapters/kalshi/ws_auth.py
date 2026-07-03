"""Kalshi Demo WebSocket read-only authentication helpers."""

from __future__ import annotations

import base64
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

KALSHI_WS_PATH = "/trade-api/ws/v2"
KALSHI_DEMO_WS_URL = "wss://external-api-ws.demo.kalshi.co/trade-api/ws/v2"
KALSHI_DEMO_API_KEY_ID_ENV = "KALSHI_DEMO_API_KEY_ID"
KALSHI_DEMO_PRIVATE_KEY_PATH_ENV = "KALSHI_DEMO_PRIVATE_KEY_PATH"


class KalshiWsAuthBlocked(Exception):
    """Raised when read-only WebSocket auth cannot be prepared safely."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class KalshiWsAuthConfig:
    """Environment-loaded read-only WebSocket credential pointers."""

    api_key_id: str
    private_key_path: Path

    @property
    def credential_presence(self) -> dict[str, bool]:
        return {
            "access_id_present": bool(self.api_key_id),
            "signing_material_present": True,
        }


def load_kalshi_ws_auth_config_from_env(
    environ: Mapping[str, str] | None = None,
) -> KalshiWsAuthConfig:
    env = environ or os.environ
    key_id = env.get(KALSHI_DEMO_API_KEY_ID_ENV)
    key_path = env.get(KALSHI_DEMO_PRIVATE_KEY_PATH_ENV)
    if not key_id or not key_path:
        raise KalshiWsAuthBlocked("NO_WS_CREDENTIALS")
    return KalshiWsAuthConfig(api_key_id=key_id, private_key_path=Path(key_path))


def build_kalshi_ws_headers(
    config: KalshiWsAuthConfig,
    *,
    timestamp_ms: int,
) -> dict[str, str]:
    key = _load_private_key(config.private_key_path)
    message = f"{timestamp_ms}GET{KALSHI_WS_PATH}".encode()
    signature = key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256(),
    )
    return {
        "KALSHI-ACCESS-KEY": config.api_key_id,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("ascii"),
        "KALSHI-ACCESS-TIMESTAMP": str(timestamp_ms),
    }


def _load_private_key(path: Path) -> rsa.RSAPrivateKey:
    try:
        payload = path.read_bytes()
        key = serialization.load_pem_private_key(payload, password=None)
    except (OSError, ValueError, TypeError) as exc:
        raise KalshiWsAuthBlocked("WS_PRIVATE_KEY_LOAD_FAILED") from exc
    if not isinstance(key, rsa.RSAPrivateKey):
        raise KalshiWsAuthBlocked("WS_PRIVATE_KEY_LOAD_FAILED")
    return key
