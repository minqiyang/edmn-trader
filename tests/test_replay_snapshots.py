from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from edmn_trader.core.models import NormalizedOrderBook, OrderBookLevel
from edmn_trader.data import MarketDataSnapshot, ReplayOrderingError, ReplaySession, write_snapshots
from edmn_trader.scripts.record_fixture_snapshots import build_fixture_snapshots
from edmn_trader.scripts.replay_snapshots import render_metrics_table

FIXTURES = Path(__file__).parent / "fixtures"


def test_replay_strict_mode_rejects_out_of_order_observed_timestamps(tmp_path: Path) -> None:
    path = tmp_path / "out_of_order.jsonl"
    later = _snapshot(observed_at=datetime(2026, 6, 11, 10, 1, tzinfo=UTC))
    earlier = _snapshot(observed_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC))
    write_snapshots(path, [later, earlier])

    with pytest.raises(ReplayOrderingError, match="out of order"):
        ReplaySession.from_path(path, strict=True)


def test_replay_non_strict_mode_sorts_and_warns(tmp_path: Path) -> None:
    path = tmp_path / "sorted.jsonl"
    later = _snapshot(ticker="LATER", observed_at=datetime(2026, 6, 11, 10, 1, tzinfo=UTC))
    earlier = _snapshot(ticker="EARLIER", observed_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC))
    write_snapshots(path, [later, earlier])

    with pytest.warns(RuntimeWarning, match="sorted"):
        session = ReplaySession.from_path(path, strict=False)

    assert [snapshot.ticker for snapshot in session.snapshots] == ["EARLIER", "LATER"]


def test_replay_metrics_expose_book_state(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    snapshot = _snapshot()
    write_snapshots(path, [snapshot])

    [metric] = ReplaySession.from_path(path).metrics()

    assert metric.best_bid == Decimal("0.4200")
    assert metric.best_ask == Decimal("0.4400")
    assert metric.spread == Decimal("0.0200")
    assert metric.mid == Decimal("0.4300")
    assert metric.bid_depth == Decimal("13.00")
    assert metric.ask_depth == Decimal("17.00")
    assert metric.bid_level_count == 1
    assert metric.ask_level_count == 1


def test_fixture_to_snapshot_conversion_is_offline_and_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "fixture_snapshots.jsonl"
    observed_at = datetime(2026, 6, 11, 0, 0, tzinfo=UTC)
    snapshots = build_fixture_snapshots(
        fixtures_dir=FIXTURES,
        observed_at=observed_at,
        recorded_at=observed_at + timedelta(seconds=1),
    )
    write_snapshots(output, snapshots)

    loaded_session = ReplaySession.from_path(output)
    [metric] = loaded_session.metrics()
    table = render_metrics_table([metric])

    assert snapshots[0].source_type == "fixture"
    assert snapshots[0].raw_payload is not None
    assert snapshots[0].raw_payload["market_ticker"] == "DEMO-EVENT-MARKET"
    assert metric.ticker == "DEMO-EVENT-MARKET"
    assert metric.best_bid == Decimal("0.4200")
    assert "DEMO-EVENT-MARKET" in table
    assert "0.0200" in table


def _snapshot(
    *,
    ticker: str = "DEMO-EVENT-MARKET",
    observed_at: datetime = datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
) -> MarketDataSnapshot:
    return MarketDataSnapshot(
        exchange="kalshi_demo",
        ticker=ticker,
        observed_at=observed_at,
        recorded_at=observed_at + timedelta(seconds=1),
        normalized_orderbook=NormalizedOrderBook(
            instrument_id=ticker,
            bids=(OrderBookLevel(price=Decimal("0.4200"), quantity=Decimal("13.00")),),
            asks=(OrderBookLevel(price=Decimal("0.4400"), quantity=Decimal("17.00")),),
            source="test",
        ),
        raw_payload={"orderbook_fp": {"yes_dollars": [], "no_dollars": []}},
        source_type="fixture",
        tags=("test",),
    )
