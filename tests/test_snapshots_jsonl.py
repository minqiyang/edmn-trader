from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from edmn_trader.core.models import NormalizedOrderBook, OrderBookLevel
from edmn_trader.data import (
    JSONLDecodeError,
    MarketDataSnapshot,
    append_snapshot,
    read_snapshots,
    write_snapshots,
)
from edmn_trader.data.jsonl import read_jsonl_records


def test_snapshot_jsonl_roundtrip_preserves_orderbook(tmp_path: Path) -> None:
    path = tmp_path / "roundtrip.jsonl"
    snapshot = _snapshot()
    write_snapshots(path, [snapshot])

    loaded = read_snapshots(path)

    assert loaded == [snapshot]


def test_snapshot_jsonl_decimal_precision_is_serialized_as_strings(tmp_path: Path) -> None:
    path = tmp_path / "snapshots.jsonl"
    snapshot = _snapshot(bid_price=Decimal("0.3333"), ask_price=Decimal("0.3334"))

    write_snapshots(path, [snapshot])

    raw_text = path.read_text(encoding="utf-8")
    assert '"price":"0.3333"' in raw_text
    assert '"price":"0.3334"' in raw_text
    assert read_snapshots(path)[0].normalized_orderbook.mid == Decimal("0.33335")


def test_malformed_jsonl_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"ok": true}\nnot-json\n', encoding="utf-8")

    with pytest.raises(JSONLDecodeError) as exc_info:
        list(read_jsonl_records(path))

    assert exc_info.value.line_number == 2
    assert "malformed JSON" in str(exc_info.value)


def test_append_snapshot_preserves_existing_records(tmp_path: Path) -> None:
    path = tmp_path / "append.jsonl"
    first = _snapshot(ticker="DEMO-1")
    second = _snapshot(ticker="DEMO-2")

    append_snapshot(path, first)
    append_snapshot(path, second)

    loaded = read_snapshots(path)
    assert [snapshot.ticker for snapshot in loaded] == ["DEMO-1", "DEMO-2"]


def test_snapshot_rejects_raw_payload_secrets() -> None:
    with pytest.raises(ValueError, match="credentials"):
        _snapshot(raw_payload={"events": [{"headers": {"authorization": "do-not-store"}}]})


def _snapshot(
    *,
    ticker: str = "DEMO-EVENT-MARKET",
    bid_price: Decimal = Decimal("0.4200"),
    ask_price: Decimal = Decimal("0.4400"),
    raw_payload: dict[str, object] | None = None,
) -> MarketDataSnapshot:
    return MarketDataSnapshot(
        exchange="kalshi_demo",
        ticker=ticker,
        observed_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
        recorded_at=datetime(2026, 6, 11, 10, 1, tzinfo=UTC),
        normalized_orderbook=NormalizedOrderBook(
            instrument_id=ticker,
            bids=(OrderBookLevel(price=bid_price, quantity=Decimal("13.00")),),
            asks=(OrderBookLevel(price=ask_price, quantity=Decimal("17.00")),),
            source="test",
        ),
        raw_payload=raw_payload or {"orderbook_fp": {"yes_dollars": [], "no_dollars": []}},
        source_type="fixture",
        tags=("test",),
    )
