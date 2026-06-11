"""Replay a local Kalshi-style orderbook fixture."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from edmn_trader.adapters.kalshi import normalize_kalshi_orderbook_fp


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=Path("tests/fixtures/kalshi_orderbook_fp_basic.json"),
        help="Path to a local Kalshi-style JSON fixture.",
    )
    args = parser.parse_args()

    raw = json.loads(args.fixture.read_text(encoding="utf-8"))
    book = normalize_kalshi_orderbook_fp(raw)

    print(f"best_yes_bid={_format_optional_decimal(book.best_bid_price)}")
    print(f"implied_yes_ask={_format_optional_decimal(book.best_ask_price)}")
    print(f"spread={_format_optional_decimal(book.spread)}")
    print(f"mid={_format_optional_decimal(book.mid)}")
    print(f"bid_depth={book.bid_depth}")
    print(f"ask_depth={book.ask_depth}")


def _format_optional_decimal(value: Decimal | None) -> str:
    return "None" if value is None else str(value)


if __name__ == "__main__":
    main()
