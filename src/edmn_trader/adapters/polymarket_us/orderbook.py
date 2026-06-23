"""Polymarket US market-book normalization helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from edmn_trader.core.models import NormalizedOrderBook, OrderBookLevel

ZERO = Decimal("0")


class PolymarketUSResponseError(ValueError):
    """Raised when a Polymarket US public response cannot be normalized."""


class PolymarketUSEmptyOrderBookError(PolymarketUSResponseError):
    """Raised when a public market book has no bid or offer levels."""


def normalize_polymarket_us_market_book(raw: dict[str, Any]) -> NormalizedOrderBook:
    """Normalize a Polymarket US public market book into the canonical book."""

    market_data = raw.get("marketData")
    if not isinstance(market_data, dict):
        msg = "Polymarket US payload must contain a marketData object"
        raise PolymarketUSResponseError(msg)

    bids = _parse_levels(market_data.get("bids"), field_name="bids")
    asks = _parse_levels(market_data.get("offers"), field_name="offers")
    if not bids and not asks:
        msg = (
            f"Polymarket US book for {_instrument_id(market_data)} "
            "contains no bid or offer levels"
        )
        raise PolymarketUSEmptyOrderBookError(msg)

    return NormalizedOrderBook(
        instrument_id=_instrument_id(market_data),
        bids=tuple(sorted(bids, key=lambda level: level.price, reverse=True)),
        asks=tuple(sorted(asks, key=lambda level: level.price)),
        source="polymarket_us_market_book",
    )


def _parse_levels(raw_levels: Any, *, field_name: str) -> list[OrderBookLevel]:
    if raw_levels is None:
        return []
    if not isinstance(raw_levels, list):
        msg = f"Polymarket US {field_name} must be a list"
        raise PolymarketUSResponseError(msg)

    levels: list[OrderBookLevel] = []
    for raw_level in raw_levels:
        if not isinstance(raw_level, dict):
            msg = f"Polymarket US {field_name} levels must be objects"
            raise PolymarketUSResponseError(msg)
        levels.append(
            OrderBookLevel(
            price=_parse_amount(raw_level.get("px"), field_name=f"{field_name} price"),
            quantity=_parse_amount(raw_level.get("qty"), field_name=f"{field_name} quantity"),
        )
        )
    return levels


def _parse_amount(raw_amount: Any, *, field_name: str) -> Decimal:
    value = raw_amount.get("value") if isinstance(raw_amount, dict) else raw_amount
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        msg = f"Polymarket US {field_name} must be decimal-compatible"
        raise PolymarketUSResponseError(msg) from exc
    if parsed < ZERO:
        msg = f"Polymarket US {field_name} must be non-negative"
        raise PolymarketUSResponseError(msg)
    return parsed


def _instrument_id(market_data: dict[str, Any]) -> str:
    for key in ("marketSlug", "slug", "id"):
        value = market_data.get(key)
        if isinstance(value, str) and value:
            return value
    return "UNKNOWN"
