"""Replay JSONL market-data snapshots and print book metrics."""

from __future__ import annotations

import argparse
from decimal import Decimal
from pathlib import Path

from edmn_trader.data.replay import ReplayMetrics, ReplaySession


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input JSONL snapshot path.")
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Sort out-of-order snapshots by observed timestamp instead of failing.",
    )
    args = parser.parse_args()

    session = ReplaySession.from_path(args.input, strict=not args.no_strict)
    print(render_metrics_table(session.metrics()))


def render_metrics_table(metrics: list[ReplayMetrics]) -> str:
    """Render a concise replay metrics table."""

    headers = [
        "seq",
        "observed_at",
        "exchange",
        "ticker",
        "bid",
        "ask",
        "spread",
        "mid",
        "bid_depth",
        "ask_depth",
        "bid_levels",
        "ask_levels",
    ]
    rows = [
        [
            str(index),
            metric.observed_at.isoformat(),
            metric.exchange,
            metric.ticker,
            _fmt(metric.best_bid),
            _fmt(metric.best_ask),
            _fmt(metric.spread),
            _fmt(metric.mid),
            _fmt(metric.bid_depth),
            _fmt(metric.ask_depth),
            str(metric.bid_level_count),
            str(metric.ask_level_count),
        ]
        for index, metric in enumerate(metrics, start=1)
    ]

    if not rows:
        return "no snapshots"

    widths = [
        max(len(row[index]) for row in [headers, *rows])
        for index in range(len(headers))
    ]
    lines = [
        " | ".join(cell.ljust(width) for cell, width in zip(headers, widths, strict=True)),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(
        " | ".join(cell.ljust(width) for cell, width in zip(row, widths, strict=True))
        for row in rows
    )
    return "\n".join(lines)


def _fmt(value: Decimal | None) -> str:
    return "" if value is None else str(value)


if __name__ == "__main__":
    main()
