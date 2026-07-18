from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from edmn_trader.cli.monitor import build_monitor_snapshot, main

NOW = datetime(2026, 7, 3, 17, 0, tzinfo=UTC)


def test_monitor_warns_without_crashing_on_corrupt_jsonl(tmp_path: Path) -> None:
    (tmp_path / "corrupt.jsonl").write_text("{invalid\n", encoding="utf-8")

    snapshot = build_monitor_snapshot(tmp_path, now=NOW)

    assert any(
        warning.startswith("CORRUPT_JSONL: corrupt.jsonl")
        for warning in snapshot["run_info"]["warnings"]
    )


@pytest.mark.parametrize(
    ("name", "payload"),
    [
        ("risk_summary.json", {"kill_switch": True}),
        ("reconciliation_summary.json", {"status": "mismatch", "mismatch_count": 1}),
    ],
)
def test_monitor_blocks_risk_and_reconciliation_failures(
    tmp_path: Path,
    name: str,
    payload: dict[str, object],
) -> None:
    (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")

    snapshot = build_monitor_snapshot(tmp_path, now=NOW)

    assert snapshot["run_info"]["health"] == "BLOCKED"


def test_monitor_export_does_not_expose_secret_like_fields(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "synthetic.jsonl").write_text(
        json.dumps(
            {
                "record_type": "paper_position",
                "market_ticker": "SYNTHETIC-MARKET",
                "market_title": {"api_token": "SYNTHETIC"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    export_path = tmp_path / "snapshot.json"

    main(
        [
            "--once",
            "--input-dir",
            str(tmp_path),
            "--format",
            "json",
            "--export-json",
            str(export_path),
        ]
    )

    exported = export_path.read_text(encoding="utf-8")
    assert '"api_token": "[REDACTED]"' in exported
    assert '"api_token": "SYNTHETIC"' not in exported
    assert '"api_token": "SYNTHETIC"' not in capsys.readouterr().out
