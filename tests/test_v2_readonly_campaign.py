from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from edmn_trader.adapters.kalshi import KalshiDemoMarketDataClient, KalshiReadOnlyOptInRequired
from edmn_trader.cli.monitor import build_monitor_snapshot, render_snapshot
from edmn_trader.scripts.v2_readonly_campaign import (
    SEVEN_DAY_SECONDS,
    evaluate_market_selection,
    plan_campaign,
    plan_kalshi_ws_campaign,
    run_kalshi_rest_smoke,
    run_kalshi_ws_smoke,
    run_smoke,
    validate_campaign,
)

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 7, 3, 18, 0, tzinfo=UTC)


def _market_metadata(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "ticker": "DEMO-EVENT-MARKET",
        "event_ticker": "DEMO-EVENT",
        "title": "Demo event market",
        "status": "open",
        "open_time": "2026-07-01T00:00:00Z",
        "close_time": "2026-07-20T00:00:00Z",
        "orderbook_level_count": 2,
    }
    payload.update(overrides)
    return payload


def test_market_selection_accepts_open_market_beyond_campaign_end() -> None:
    result = evaluate_market_selection(
        _market_metadata(),
        selected_at_utc=NOW,
        duration_seconds=SEVEN_DAY_SECONDS,
    )

    assert result["selection_gate_result"] == "pass"
    assert result["selection_gate_rejection_reason"] is None
    assert result["market_ticker"] == "DEMO-EVENT-MARKET"


def test_market_selection_rejects_finalized_market() -> None:
    result = evaluate_market_selection(
        _market_metadata(status="finalized"),
        selected_at_utc=NOW,
        duration_seconds=SEVEN_DAY_SECONDS,
    )

    assert result["selection_gate_result"] == "reject"
    assert result["selection_gate_rejection_reason"] == "MARKET_STATUS_FINALIZED"


def test_market_selection_rejects_closed_and_settled_markets() -> None:
    for status, reason in (
        ("closed", "MARKET_STATUS_CLOSED"),
        ("settled", "MARKET_STATUS_SETTLED"),
    ):
        result = evaluate_market_selection(
            _market_metadata(status=status),
            selected_at_utc=NOW,
            duration_seconds=SEVEN_DAY_SECONDS,
        )

        assert result["selection_gate_rejection_reason"] == reason


def test_market_selection_rejects_short_close_window() -> None:
    result = evaluate_market_selection(
        _market_metadata(close_time="2026-07-08T00:00:00Z"),
        selected_at_utc=NOW,
        duration_seconds=SEVEN_DAY_SECONDS,
    )

    assert result["selection_gate_rejection_reason"] == "TIME_TO_CLOSE_TOO_SHORT"


def test_market_selection_rejects_missing_close_time_and_empty_orderbook() -> None:
    missing_close = _market_metadata()
    del missing_close["close_time"]

    assert (
        evaluate_market_selection(
            missing_close,
            selected_at_utc=NOW,
            duration_seconds=SEVEN_DAY_SECONDS,
        )["selection_gate_rejection_reason"]
        == "MISSING_CLOSE_TIME"
    )
    assert (
        evaluate_market_selection(
            _market_metadata(orderbook_level_count=0),
            selected_at_utc=NOW,
            duration_seconds=SEVEN_DAY_SECONDS,
        )["selection_gate_rejection_reason"]
        == "EMPTY_ORDERBOOK"
    )


def test_campaign_smoke_writes_bounded_readonly_artifacts(tmp_path: Path) -> None:
    result = run_smoke(
        output_dir=tmp_path,
        campaign_id="c1",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )

    assert result["validation_status"] == "pass"
    assert result["heartbeat_count"] == 3
    summary = json.loads((tmp_path / "campaign_summary.json").read_text(encoding="utf-8"))
    assert summary["live_gate_status"] == "disabled"
    assert summary["submit_attempt_count"] == 0
    assert (tmp_path / "campaign_validation.json").exists()


def test_kalshi_rest_smoke_runs_recorder_rebuild_and_validation(tmp_path: Path) -> None:
    client = _kalshi_client()

    result = run_kalshi_rest_smoke(
        output_dir=tmp_path,
        campaign_id="c1",
        market="DEMO-EVENT-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        live_readonly_opt_in=True,
        client=client,
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )

    assert result["validation_status"] == "pass"
    assert result["recorder_event_count"] == 1
    assert result["rebuild_frame_count"] == 1
    assert result["daily_validation_count"] == 1
    validation = json.loads((tmp_path / "campaign_validation.json").read_text(encoding="utf-8"))
    assert validation["evidence_classification"] == "LAYER1_REST_SMOKE_PASS"
    snapshot = build_monitor_snapshot(tmp_path, now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC))
    rendered = render_snapshot(snapshot, "table")
    assert snapshot["evidence"]["layers"]["Layer 1 recorder"] == "pass"
    assert snapshot["evidence"]["layers"]["Layer 2 replay/simulator"] == "pass"
    assert snapshot["campaign"]["status"] == "REST_SMOKE"
    assert "events=1" in rendered
    assert "rebuild_frames=1" in rendered


def test_kalshi_rest_smoke_requires_opt_in_before_http(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    client = _kalshi_client(requests=requests)

    with pytest.raises(KalshiReadOnlyOptInRequired, match="--live-readonly-opt-in"):
        run_kalshi_rest_smoke(
            output_dir=tmp_path,
            campaign_id="c1",
            market="DEMO-EVENT-MARKET",
            duration_seconds=30,
            interval_seconds=10,
            live_readonly_opt_in=False,
            client=client,
        )

    assert requests == []


def test_campaign_validator_fails_secret_like_fields(tmp_path: Path) -> None:
    plan_campaign(
        root=tmp_path,
        campaign_id="c1",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )
    (tmp_path / "campaign_heartbeat.jsonl").write_text(
        '{"record_type":"campaign_heartbeat","api_token":"nope"}\n',
        encoding="utf-8",
    )

    result = validate_campaign(input_dir=tmp_path)

    assert result["status"] == "fail"
    assert "secret-like field found in campaign artifacts" in result["failures"]


def test_campaign_duration_is_bounded(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="between 1 and 600"):
        plan_campaign(
            root=tmp_path,
            campaign_id="c1",
            venue="kalshi_demo",
            market="DEMO-MARKET",
            duration_seconds=601,
            interval_seconds=10,
        )


def test_kalshi_ws_smoke_truthfully_blocks_without_reviewed_ws_adapter(tmp_path: Path) -> None:
    result = run_kalshi_ws_smoke(
        output_dir=tmp_path,
        campaign_id="round6_kalshi_ws_smoke",
        duration_seconds=300,
        max_markets=1,
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )

    assert result["validation_status"] == "blocked"
    assert result["evidence_classification"] == "LAYER1_WS_CAMPAIGN_INCOMPLETE"
    assert result["submit_attempt_count"] == 0
    assert (tmp_path / "campaign_manifest.json").exists()
    assert (tmp_path / "run_metadata.json").exists()
    validation = json.loads((tmp_path / "campaign_validation.json").read_text(encoding="utf-8"))
    assert validation["source_type"] == "WEBSOCKET_DELTA"
    assert validation["event_count"] == 0
    snapshot = build_monitor_snapshot(tmp_path, now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC))
    rendered = render_snapshot(snapshot, "table")
    assert snapshot["campaign"]["status"] == "NO_DATA"
    assert snapshot["campaign"]["source_type"] == "WEBSOCKET_DELTA"
    assert "validation=blocked" in rendered


def test_validator_classifies_websocket_smoke_only_when_ws_events_exist(
    tmp_path: Path,
) -> None:
    plan_campaign(
        root=tmp_path,
        campaign_id="ws1",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=300,
        interval_seconds=10,
        source_type="WEBSOCKET_DELTA",
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )
    summary = json.loads((tmp_path / "campaign_summary.json").read_text(encoding="utf-8"))
    summary.update(
        {
            "status": "websocket_smoke_complete",
            "event_count": 2,
            "delta_count": 1,
            "snapshot_count": 1,
            "rebuild_frame_count": 2,
            "last_event_time": "2026-07-03T18:00:00+00:00",
        }
    )
    (tmp_path / "campaign_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (tmp_path / "campaign_heartbeat.jsonl").write_text(
        json.dumps(
            {
                "record_type": "campaign_heartbeat",
                "campaign_id": "ws1",
                "venue": "kalshi_demo",
                "market": "DEMO-MARKET",
                "sequence": 1,
                "observed_at": "2026-07-03T18:00:00+00:00",
                "received_at": "2026-07-03T18:00:00+00:00",
                "source_type": "WEBSOCKET_DELTA",
                "live_gate_status": "disabled",
                "submit_attempt": False,
                "production_endpoint_used": False,
                "status": "ok",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = validate_campaign(input_dir=tmp_path)

    assert result["status"] == "pass"
    assert result["evidence_classification"] == "LAYER1_WS_SMOKE_PASS"


def test_validator_blocks_finalized_market_as_campaign_evidence(tmp_path: Path) -> None:
    plan_campaign(
        root=tmp_path,
        campaign_id="ws1",
        venue="kalshi_demo",
        market="DEMO-EVENT-MARKET",
        duration_seconds=300,
        interval_seconds=10,
        source_type="WEBSOCKET_DELTA",
        now=NOW,
        market_metadata=_market_metadata(status="finalized"),
    )
    summary = json.loads((tmp_path / "campaign_summary.json").read_text(encoding="utf-8"))
    summary.update(
        {
            "status": "websocket_smoke_complete",
            "event_count": 2,
            "delta_count": 1,
            "snapshot_count": 1,
            "rebuild_frame_count": 2,
            "last_event_time": NOW.isoformat(),
        }
    )
    (tmp_path / "campaign_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    _write_ok_heartbeat(tmp_path)

    result = validate_campaign(input_dir=tmp_path)

    assert result["status"] == "pass"
    assert (
        result["evidence_classification"]
        == "MARKET_CLOSED_OR_FINALIZED_ENDS_CAMPAIGN_EVIDENCE"
    )
    assert result["data_integrity_classification"] == "DATA_INTEGRITY_PASS"
    assert result["campaign_evidence_valid"] is False


def test_ws_campaign_plan_requires_market_metadata(tmp_path: Path) -> None:
    result = plan_kalshi_ws_campaign(
        output_dir=tmp_path,
        campaign_id="seven-day",
        duration_seconds=SEVEN_DAY_SECONDS,
        max_markets=1,
        now=NOW,
    )

    assert result["selection_gate_result"] == "reject"
    assert result["selection_gate_rejection_reason"] == "MISSING_MARKET_METADATA"
    assert result["live_gate_status"] == "disabled"
    assert result["submit_attempt_count"] == 0


def test_monitor_shows_campaign_view(tmp_path: Path) -> None:
    run_smoke(
        output_dir=tmp_path,
        campaign_id="c1",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC),
    )

    snapshot = build_monitor_snapshot(tmp_path, now=datetime(2026, 7, 3, 18, 0, tzinfo=UTC))
    rendered = render_snapshot(snapshot, "table")

    assert snapshot["campaign"]["campaign_id"] == "c1"
    assert "CAMPAIGN: id=c1" in rendered
    assert "submit_attempts=0" in rendered


def test_monitor_prominently_shows_finalized_market(tmp_path: Path) -> None:
    plan_campaign(
        root=tmp_path,
        campaign_id="ws1",
        venue="kalshi_demo",
        market="DEMO-EVENT-MARKET",
        duration_seconds=300,
        interval_seconds=10,
        source_type="WEBSOCKET_DELTA",
        now=NOW,
        market_metadata=_market_metadata(status="settled"),
    )
    _write_ok_heartbeat(tmp_path)
    validate_campaign(input_dir=tmp_path)

    snapshot = build_monitor_snapshot(tmp_path, now=NOW)
    rendered = render_snapshot(snapshot, "table")

    assert snapshot["campaign"]["status"] == "MARKET_CLOSED_OR_FINALIZED"
    assert snapshot["campaign"]["subscribed_market_ticker"] == "DEMO-EVENT-MARKET"
    assert snapshot["campaign"]["market_status"] == "settled"
    assert "MARKET_CLOSED_OR_FINALIZED" in rendered
    assert "market=DEMO-EVENT-MARKET" in rendered


def test_completed_canary_quiet_market_is_not_stale_warning(tmp_path: Path) -> None:
    run_smoke(
        output_dir=tmp_path,
        campaign_id="canary",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        now=NOW,
    )

    snapshot = build_monitor_snapshot(tmp_path, now=datetime(2026, 7, 4, 18, 0, tzinfo=UTC))

    assert snapshot["data_status"]["stale_status"] == "COMPLETE"
    assert not any("STALE_DATA" in warning for warning in snapshot["run_info"]["warnings"])


def test_no_production_or_submit_path_is_added(tmp_path: Path) -> None:
    result = run_smoke(
        output_dir=tmp_path,
        campaign_id="safe",
        venue="kalshi_demo",
        market="DEMO-MARKET",
        duration_seconds=30,
        interval_seconds=10,
        now=NOW,
    )
    summary = json.loads((tmp_path / "campaign_summary.json").read_text(encoding="utf-8"))

    assert result["submit_attempt_count"] == 0
    assert summary["production_endpoint_used"] is False
    assert summary["live_gate_status"] == "disabled"


def _write_ok_heartbeat(tmp_path: Path) -> None:
    (tmp_path / "campaign_heartbeat.jsonl").write_text(
        json.dumps(
            {
                "record_type": "campaign_heartbeat",
                "campaign_id": "ws1",
                "venue": "kalshi_demo",
                "market": "DEMO-EVENT-MARKET",
                "sequence": 1,
                "observed_at": NOW.isoformat(),
                "received_at": NOW.isoformat(),
                "source_type": "WEBSOCKET_DELTA",
                "live_gate_status": "disabled",
                "submit_attempt": False,
                "production_endpoint_used": False,
                "status": "ok",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _kalshi_client(requests: list[httpx.Request] | None = None) -> KalshiDemoMarketDataClient:
    payload = json.loads((FIXTURES / "kalshi_orderbook_response.json").read_text(encoding="utf-8"))

    def handler(request: httpx.Request) -> httpx.Response:
        if requests is not None:
            requests.append(request)
        return httpx.Response(200, json=payload)

    return KalshiDemoMarketDataClient(
        http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
