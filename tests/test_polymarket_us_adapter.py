from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from edmn_trader.adapters.polymarket_us import (
    PolymarketUSConfigurationError,
    PolymarketUSEmptyOrderBookError,
    PolymarketUSMarketDataClient,
    PolymarketUSResponseError,
    normalize_polymarket_us_market_book,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_polymarket_us_fixture_normalizes_to_canonical_orderbook() -> None:
    book = normalize_polymarket_us_market_book(_load_fixture("polymarket_us_market_book.json"))

    assert book.instrument_id == "will-fed-cut-rates-in-september"
    assert book.source == "polymarket_us_market_book"
    assert book.best_bid_price == Decimal("0.4200")
    assert book.best_ask_price == Decimal("0.4400")
    assert book.spread == Decimal("0.0200")
    assert book.bid_depth == Decimal("15.00")
    assert book.ask_depth == Decimal("20.00")


def test_polymarket_us_client_uses_public_read_only_book_endpoint() -> None:
    requests: list[httpx.Request] = []
    payload = _load_fixture("polymarket_us_market_book.json")

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=payload)

    client = PolymarketUSMarketDataClient(
        http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    book = client.get_normalized_orderbook("will-fed-cut-rates-in-september")

    assert book.best_bid_price == Decimal("0.4200")
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/v1/markets/will-fed-cut-rates-in-september/book"
    assert "authorization" not in requests[0].headers
    assert requests[0].url.host == "gateway.polymarket.us"


def test_polymarket_us_client_rejects_international_base_url() -> None:
    with pytest.raises(PolymarketUSConfigurationError, match="public base URL"):
        PolymarketUSMarketDataClient(base_url="https://gamma-api.polymarket.com")


def test_polymarket_us_parser_rejects_empty_orderbook() -> None:
    payload = {"marketData": {"marketSlug": "empty", "bids": [], "offers": []}}

    with pytest.raises(PolymarketUSEmptyOrderBookError, match="contains no bid or offer levels"):
        normalize_polymarket_us_market_book(payload)


def test_polymarket_us_parser_rejects_malformed_levels() -> None:
    payload = {"marketData": {"marketSlug": "bad", "bids": [{"px": {}}], "offers": []}}

    with pytest.raises(PolymarketUSResponseError, match="price"):
        normalize_polymarket_us_market_book(payload)


def _load_fixture(name: str) -> dict[str, Any]:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"{name} must contain a JSON object"
        raise TypeError(msg)
    return payload
