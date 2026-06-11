"""Convert local Kalshi fixtures into JSONL market-data snapshots."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from edmn_trader.adapters.kalshi import normalize_kalshi_orderbook_fp
from edmn_trader.data.snapshots import MarketDataSnapshot, write_snapshots

DEFAULT_OBSERVED_AT = "2026-06-11T00:00:00+00:00"
DEFAULT_RECORDED_AT = "2026-06-11T00:00:00+00:00"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Output JSONL snapshot path.")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=_repo_root() / "tests" / "fixtures",
        help="Directory containing local Kalshi JSON fixtures.",
    )
    parser.add_argument(
        "--observed-at",
        default=DEFAULT_OBSERVED_AT,
        help="Timezone-aware ISO observed timestamp for fixture snapshots.",
    )
    parser.add_argument(
        "--recorded-at",
        default=DEFAULT_RECORDED_AT,
        help="Timezone-aware ISO local recorded timestamp for fixture snapshots.",
    )
    args = parser.parse_args()

    snapshots = build_fixture_snapshots(
        fixtures_dir=args.fixtures_dir,
        observed_at=_parse_datetime(args.observed_at, "--observed-at"),
        recorded_at=_parse_datetime(args.recorded_at, "--recorded-at"),
    )
    write_snapshots(args.output, snapshots)
    print(f"wrote {len(snapshots)} snapshot(s) to {args.output}")


def build_fixture_snapshots(
    *,
    fixtures_dir: Path,
    observed_at: datetime,
    recorded_at: datetime,
) -> list[MarketDataSnapshot]:
    """Build deterministic snapshots from committed local Kalshi fixtures."""

    markets_payload = _load_json_object(fixtures_dir / "kalshi_markets_response.json")
    orderbook_payload = _load_json_object(fixtures_dir / "kalshi_orderbook_response.json")
    ticker = _ticker_from_markets_payload(markets_payload)

    raw_payload = dict(orderbook_payload)
    raw_payload["market_ticker"] = ticker
    normalized_book = normalize_kalshi_orderbook_fp(raw_payload)

    return [
        MarketDataSnapshot(
            exchange="kalshi_demo",
            ticker=ticker,
            observed_at=observed_at,
            recorded_at=recorded_at,
            normalized_orderbook=normalized_book,
            raw_payload=raw_payload,
            source_type="fixture",
            notes="Recorded from committed local Kalshi fixture; no network call.",
            tags=("stage3", "fixture", "kalshi_demo"),
        )
    ]


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"{path} must contain a JSON object"
        raise ValueError(msg)
    return payload


def _ticker_from_markets_payload(payload: dict[str, Any]) -> str:
    markets = payload.get("markets")
    if not isinstance(markets, list) or not markets:
        msg = "markets fixture must contain at least one market"
        raise ValueError(msg)

    first_market = markets[0]
    if not isinstance(first_market, dict):
        msg = "markets fixture first market must be an object"
        raise ValueError(msg)

    ticker = first_market.get("ticker")
    if not isinstance(ticker, str) or not ticker:
        msg = "markets fixture first market must include a ticker"
        raise ValueError(msg)
    return ticker


def _parse_datetime(value: str, field_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        msg = f"{field_name} must be timezone-aware"
        raise ValueError(msg)
    return parsed


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


if __name__ == "__main__":
    main()
