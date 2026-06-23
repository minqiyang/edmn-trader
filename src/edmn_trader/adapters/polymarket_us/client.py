"""Read-only Polymarket US public market-data client."""

from __future__ import annotations

from typing import Any, Self
from urllib.parse import quote

import httpx

from edmn_trader.adapters.polymarket_us.orderbook import (
    PolymarketUSResponseError,
    normalize_polymarket_us_market_book,
)
from edmn_trader.core.models import NormalizedOrderBook

POLYMARKET_US_PUBLIC_BASE_URL = "https://gateway.polymarket.us"
_USER_AGENT = "edmn-trader/0.1 read-only-polymarket-us-client"


class PolymarketUSClientError(Exception):
    """Base class for Polymarket US adapter client errors."""


class PolymarketUSConfigurationError(PolymarketUSClientError):
    """Raised when client configuration leaves the public market-data boundary."""


class PolymarketUSHTTPError(PolymarketUSClientError):
    """Raised for non-success HTTP status codes from Polymarket US public API."""

    def __init__(self, *, status_code: int, path: str, body: str) -> None:
        self.status_code = status_code
        self.path = path
        self.body = body
        super().__init__(f"Polymarket US GET {path} returned HTTP {status_code}: {body}")


class PolymarketUSMarketDataClient:
    """Guarded read-only client for Polymarket US public market-data endpoints."""

    def __init__(
        self,
        *,
        base_url: str = POLYMARKET_US_PUBLIC_BASE_URL,
        timeout: float = 10.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.base_url = _normalize_base_url(base_url)
        _validate_public_base_url(self.base_url)

        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT},
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client when this instance owns it."""

        if self._owns_client:
            self._client.close()

    def get_market_book(self, slug: str) -> dict[str, Any]:
        """Return one raw public Polymarket US market book by slug."""

        clean_slug = _validate_slug(slug)
        payload = self._get_json(f"/v1/markets/{quote(clean_slug, safe='')}/book")
        if not isinstance(payload.get("marketData"), dict):
            msg = "Polymarket US market book response must contain a marketData object"
            raise PolymarketUSResponseError(msg)
        return payload

    def get_normalized_orderbook(self, slug: str) -> NormalizedOrderBook:
        """Return a canonical orderbook for one Polymarket US market slug."""

        return normalize_polymarket_us_market_book(self.get_market_book(slug))

    def _get_json(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        try:
            response = self._client.get(url)
        except httpx.HTTPError as exc:
            msg = f"Polymarket US GET {path} failed before a response was received: {exc}"
            raise PolymarketUSClientError(msg) from exc

        if response.status_code >= 400:
            raise PolymarketUSHTTPError(
                status_code=response.status_code,
                path=path,
                body=_short_body(response.text),
            )

        try:
            payload = response.json()
        except ValueError as exc:
            msg = f"Polymarket US GET {path} returned malformed JSON"
            raise PolymarketUSResponseError(msg) from exc

        if not isinstance(payload, dict):
            msg = f"Polymarket US GET {path} returned a non-object JSON payload"
            raise PolymarketUSResponseError(msg)
        return payload


def _normalize_base_url(base_url: str) -> str:
    clean_url = base_url.rstrip("/")
    if not clean_url:
        msg = "base_url is required"
        raise PolymarketUSConfigurationError(msg)
    return clean_url


def _validate_public_base_url(base_url: str) -> None:
    if base_url != POLYMARKET_US_PUBLIC_BASE_URL:
        msg = (
            "Polymarket US client is restricted to the public base URL: "
            f"{POLYMARKET_US_PUBLIC_BASE_URL}"
        )
        raise PolymarketUSConfigurationError(msg)


def _validate_slug(slug: str) -> str:
    clean_slug = slug.strip()
    if not clean_slug:
        msg = "slug is required"
        raise ValueError(msg)
    return clean_slug


def _short_body(body: str, *, max_chars: int = 300) -> str:
    clean_body = body.strip()
    if len(clean_body) <= max_chars:
        return clean_body
    return f"{clean_body[:max_chars]}..."
