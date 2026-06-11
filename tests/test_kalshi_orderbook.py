from decimal import Decimal

import pytest

from edmn_trader.adapters.kalshi import normalize_kalshi_orderbook_fp


def test_basic_yes_no_conversion() -> None:
    book = normalize_kalshi_orderbook_fp(
        {
            "market_ticker": "DEMO",
            "orderbook_fp": {
                "yes_dollars": [["0.4200", "13.00"]],
                "no_dollars": [["0.5600", "17.00"]],
            },
        }
    )

    assert book.instrument_id == "DEMO"
    assert book.best_bid_price == Decimal("0.4200")
    assert book.best_ask_price == Decimal("0.4400")
    assert book.spread == Decimal("0.0200")
    assert book.mid == Decimal("0.4300")
    assert book.bid_depth == Decimal("13.00")
    assert book.ask_depth == Decimal("17.00")


def test_empty_yes_dollars_has_no_bid() -> None:
    book = normalize_kalshi_orderbook_fp(
        {
            "orderbook_fp": {
                "yes_dollars": [],
                "no_dollars": [["0.5600", "17.00"]],
            },
        }
    )

    assert book.best_bid is None
    assert book.best_ask_price == Decimal("0.4400")
    assert book.spread is None
    assert book.mid is None
    assert book.bid_depth == Decimal("0")
    assert book.ask_depth == Decimal("17.00")


def test_empty_no_dollars_has_no_ask() -> None:
    book = normalize_kalshi_orderbook_fp(
        {
            "orderbook_fp": {
                "yes_dollars": [["0.4200", "13.00"]],
                "no_dollars": [],
            },
        }
    )

    assert book.best_bid_price == Decimal("0.4200")
    assert book.best_ask is None
    assert book.spread is None
    assert book.mid is None
    assert book.bid_depth == Decimal("13.00")
    assert book.ask_depth == Decimal("0")


def test_multiple_price_levels_are_sorted_and_depth_is_aggregated() -> None:
    book = normalize_kalshi_orderbook_fp(
        {
            "orderbook_fp": {
                "yes_dollars": [
                    ["0.4100", "10.00"],
                    ["0.4200", "13.00"],
                    ["0.3900", "2.00"],
                ],
                "no_dollars": [
                    ["0.5300", "5.00"],
                    ["0.5500", "17.00"],
                    ["0.5400", "3.00"],
                ],
            },
        }
    )

    assert [level.price for level in book.bids] == [
        Decimal("0.4200"),
        Decimal("0.4100"),
        Decimal("0.3900"),
    ]
    assert [level.price for level in book.asks] == [
        Decimal("0.4500"),
        Decimal("0.4600"),
        Decimal("0.4700"),
    ]
    assert book.best_bid_price == Decimal("0.4200")
    assert book.best_ask_price == Decimal("0.4500")
    assert book.bid_depth == Decimal("25.00")
    assert book.ask_depth == Decimal("25.00")


def test_decimal_precision_is_preserved() -> None:
    book = normalize_kalshi_orderbook_fp(
        {
            "orderbook_fp": {
                "yes_dollars": [["0.3333", "1.0000"]],
                "no_dollars": [["0.6666", "2.0000"]],
            },
        }
    )

    assert book.best_bid_price == Decimal("0.3333")
    assert book.best_ask_price == Decimal("0.3334")
    assert book.spread == Decimal("0.0001")
    assert book.mid == Decimal("0.33335")


def test_invalid_price_greater_than_one_is_rejected() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        normalize_kalshi_orderbook_fp(
            {
                "orderbook_fp": {
                    "yes_dollars": [["1.0100", "13.00"]],
                    "no_dollars": [["0.5600", "17.00"]],
                },
            }
        )


@pytest.mark.parametrize(
    ("yes_bid", "no_bid"),
    [
        ("0.5000", "0.5000"),
        ("0.6000", "0.5000"),
    ],
)
def test_locked_or_crossed_books_are_rejected(yes_bid: str, no_bid: str) -> None:
    with pytest.raises(ValueError, match="locked or crossed"):
        normalize_kalshi_orderbook_fp(
            {
                "orderbook_fp": {
                    "yes_dollars": [[yes_bid, "13.00"]],
                    "no_dollars": [[no_bid, "17.00"]],
                },
            }
        )
