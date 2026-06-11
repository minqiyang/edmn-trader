"""Deterministic replay cursor over offline market-data snapshots."""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from edmn_trader.data.snapshots import MarketDataSnapshot, read_snapshots


class ReplayOrderingError(ValueError):
    """Raised when strict replay sees out-of-order observed timestamps."""


@dataclass(frozen=True, slots=True)
class ReplayMetrics:
    """Book metrics exposed for one replayed snapshot."""

    exchange: str
    ticker: str
    observed_at: datetime
    recorded_at: datetime
    best_bid: Decimal | None
    best_ask: Decimal | None
    spread: Decimal | None
    mid: Decimal | None
    bid_depth: Decimal
    ask_depth: Decimal
    bid_level_count: int
    ask_level_count: int

    @classmethod
    def from_snapshot(cls, snapshot: MarketDataSnapshot) -> ReplayMetrics:
        book = snapshot.normalized_orderbook
        return cls(
            exchange=snapshot.exchange,
            ticker=snapshot.ticker,
            observed_at=snapshot.observed_at,
            recorded_at=snapshot.recorded_at,
            best_bid=book.best_bid_price,
            best_ask=book.best_ask_price,
            spread=book.spread,
            mid=book.mid,
            bid_depth=book.bid_depth,
            ask_depth=book.ask_depth,
            bid_level_count=len(book.bids),
            ask_level_count=len(book.asks),
        )


@dataclass(frozen=True, slots=True)
class ReplayFrame:
    """One replay cursor frame with its source snapshot and derived metrics."""

    sequence: int
    snapshot: MarketDataSnapshot
    metrics: ReplayMetrics


class ReplaySession:
    """A deterministic replay session over a snapshot sequence."""

    def __init__(self, snapshots: list[MarketDataSnapshot], *, strict: bool = True) -> None:
        self.strict = strict
        self.snapshots = _prepare_snapshots(snapshots, strict=strict)

    @classmethod
    def from_path(cls, path: Path, *, strict: bool = True) -> ReplaySession:
        """Load snapshots from JSONL and create a replay session."""

        return cls(read_snapshots(path), strict=strict)

    def __iter__(self) -> Iterator[ReplayFrame]:
        return iter(self.frames())

    def frames(self) -> list[ReplayFrame]:
        """Return replay frames with deterministic sequence numbers."""

        return [
            ReplayFrame(
                sequence=index,
                snapshot=snapshot,
                metrics=ReplayMetrics.from_snapshot(snapshot),
            )
            for index, snapshot in enumerate(self.snapshots, start=1)
        ]

    def metrics(self) -> list[ReplayMetrics]:
        """Return replay metrics for all snapshots."""

        return [frame.metrics for frame in self.frames()]


def _prepare_snapshots(
    snapshots: list[MarketDataSnapshot],
    *,
    strict: bool,
) -> list[MarketDataSnapshot]:
    if strict:
        _validate_observed_order(snapshots)
        return list(snapshots)

    if _is_observed_ordered(snapshots):
        return list(snapshots)

    warnings.warn(
        "snapshot observed_at values were out of order; non-strict replay sorted them",
        RuntimeWarning,
        stacklevel=2,
    )
    return sorted(snapshots, key=lambda snapshot: snapshot.observed_at)


def _validate_observed_order(snapshots: list[MarketDataSnapshot]) -> None:
    for previous, current in zip(snapshots, snapshots[1:], strict=False):
        if current.observed_at < previous.observed_at:
            msg = "snapshot observed_at values are out of order"
            raise ReplayOrderingError(msg)


def _is_observed_ordered(snapshots: list[MarketDataSnapshot]) -> bool:
    try:
        _validate_observed_order(snapshots)
    except ReplayOrderingError:
        return False
    return True
