"""Kalshi Demo adapter helpers."""

from edmn_trader.adapters.kalshi.client import (
    KALSHI_DEMO_REST_BASE_URL,
    KalshiClientError,
    KalshiConfigurationError,
    KalshiDemoMarketDataClient,
    KalshiEmptyOrderBookError,
    KalshiHTTPError,
    KalshiResponseError,
)
from edmn_trader.adapters.kalshi.demo_connector import (
    KalshiDemoConnectorConfig,
    KalshiDemoConnectorError,
    KalshiDemoConnectorResult,
    KalshiDemoRequestPreview,
    load_kalshi_demo_auth_headers_from_env,
    preview_or_submit_kalshi_demo,
    write_kalshi_demo_result_jsonl,
)
from edmn_trader.adapters.kalshi.orderbook import normalize_kalshi_orderbook_fp
from edmn_trader.adapters.kalshi.readonly_recorder import (
    KalshiReadOnlyOptInRequired,
    KalshiReadOnlyRecorderConfig,
    KalshiReadOnlyRecorderResult,
    record_kalshi_readonly_orderbook,
)

__all__ = [
    "KALSHI_DEMO_REST_BASE_URL",
    "KalshiClientError",
    "KalshiConfigurationError",
    "KalshiDemoConnectorConfig",
    "KalshiDemoConnectorError",
    "KalshiDemoConnectorResult",
    "KalshiDemoMarketDataClient",
    "KalshiDemoRequestPreview",
    "KalshiEmptyOrderBookError",
    "KalshiHTTPError",
    "KalshiReadOnlyOptInRequired",
    "KalshiReadOnlyRecorderConfig",
    "KalshiReadOnlyRecorderResult",
    "KalshiResponseError",
    "load_kalshi_demo_auth_headers_from_env",
    "normalize_kalshi_orderbook_fp",
    "preview_or_submit_kalshi_demo",
    "record_kalshi_readonly_orderbook",
    "write_kalshi_demo_result_jsonl",
]
