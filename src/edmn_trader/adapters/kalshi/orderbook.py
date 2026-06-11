"""Kalshi orderbook normalization helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from edmn_trader.core.models import NormalizedOrderBook, OrderBookLevel

ONE = Decimal("1")
ZERO = Decimal("0")


def normalize_kalshi_orderbook_fp(raw: dict[str, Any]) -> NormalizedOrderBook:
    """Normalize a Kalshi fixed-point YES/NO orderbook into a canonical YES book.

    Kalshi binary orderbooks expose YES bids and NO bids. A NO bid implies a YES
    ask at `1 - no_price`, preserving the available size at that level.
    """

    orderbook = raw.get("orderbook_fp")
    if not isinstance(orderbook, dict):
        msg = "Kalshi payload must contain an orderbook_fp object"
        raise ValueError(msg)

    bids = _parse_yes_bid_levels(orderbook.get("yes_dollars", []))
    asks = _parse_no_bid_levels_as_yes_asks(orderbook.get("no_dollars", []))

    return NormalizedOrderBook(
        instrument_id=_instrument_id(raw),
        bids=tuple(sorted(bids, key=lambda level: level.price, reverse=True)),
        asks=tuple(sorted(asks, key=lambda level: level.price)),
        source="kalshi_orderbook_fp",
    )


def _parse_yes_bid_levels(raw_levels: Any) -> list[OrderBookLevel]:
    return [
        OrderBookLevel(price=price, quantity=quantity)
        for price, quantity in _parse_price_quantity_levels(raw_levels, field_name="yes_dollars")
    ]


def _parse_no_bid_levels_as_yes_asks(raw_levels: Any) -> list[OrderBookLevel]:
    return [
        OrderBookLevel(price=ONE - no_price, quantity=quantity)
        for no_price, quantity in _parse_price_quantity_levels(raw_levels, field_name="no_dollars")
    ]


def _parse_price_quantity_levels(
    raw_levels: Any,
    *,
    field_name: str,
) -> list[tuple[Decimal, Decimal]]:
    if raw_levels is None:
        return []
    if not isinstance(raw_levels, list):
        msg = f"{field_name} must be a list of [price, quantity] levels"
        raise ValueError(msg)

    levels: list[tuple[Decimal, Decimal]] = []
    for raw_level in raw_levels:
        if not isinstance(raw_level, list | tuple) or len(raw_level) != 2:
            msg = f"{field_name} levels must be [price, quantity] pairs"
            raise ValueError(msg)

        price = _to_decimal(raw_level[0], field_name=f"{field_name} price")
        quantity = _to_decimal(raw_level[1], field_name=f"{field_name} quantity")
        _validate_probability_price(price, field_name=f"{field_name} price")
        levels.append((price, quantity))

    return levels


def _to_decimal(value: Any, *, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        msg = f"{field_name} must be decimal-compatible"
        raise ValueError(msg) from exc


def _validate_probability_price(price: Decimal, *, field_name: str) -> None:
    if price < ZERO or price > ONE:
        msg = f"{field_name} must be between 0 and 1"
        raise ValueError(msg)


def _instrument_id(raw: dict[str, Any]) -> str:
    for key in ("instrument_id", "market_ticker", "ticker"):
        value = raw.get(key)
        if isinstance(value, str) and value:
            return value

    orderbook = raw.get("orderbook_fp")
    if isinstance(orderbook, dict):
        for key in ("instrument_id", "market_ticker", "ticker"):
            value = orderbook.get(key)
            if isinstance(value, str) and value:
                return value

    return "UNKNOWN"
