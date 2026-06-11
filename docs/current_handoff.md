# Current Handoff

## Current project state

The repository contains a Python 3.12 package for a demo-first,
risk-controlled event-driven prediction-market research platform. Current
implemented code includes exchange-agnostic core models, Kalshi-style
fixed-point orderbook normalization, a guarded read-only Kalshi Demo REST
client, local fixtures, mocked HTTP tests, and a fixture replay script.

## Last completed stage

Stage 2: Read-only Kalshi Demo market-data client.

## Important files

- `AGENTS.md`: repo rules and first-read instructions.
- `PROJECT_SPEC.md`: stable project and module specification.
- `CHANGELOG.md`: external-facing milestone log.
- `docs/repo_map.md`: context-budget map for targeted reads.
- `docs/codex_long_running_controller.md`: staged continuation rules.
- `docs/STAGE_PLAN.md`: staged roadmap and non-goals.
- `docs/engineering_log.md`: narrative engineering record.
- `src/edmn_trader/core/models.py`: exchange-agnostic core models.
- `src/edmn_trader/adapters/kalshi/client.py`: guarded read-only Kalshi Demo
  REST client for markets and orderbooks.
- `src/edmn_trader/adapters/kalshi/orderbook.py`: Kalshi orderbook normalizer.
- `tests/test_kalshi_client.py`: mocked HTTP coverage for the Stage 2 client.
- `tests/test_kalshi_orderbook.py`: normalizer coverage.

## Commands that currently pass

```bash
pytest
ruff check .
python scripts/01_replay_orderbook_fixture.py
```

Optional environment validation:

```bash
python -m pip install -e ".[dev]"
```

## Known issues

- The repository has no remote configured by design.
- The Kalshi Demo client is tested with mocked HTTP and local fixtures; no live
  network smoke script exists.
- No strategy, execution engine, WebSocket ingestion, or production trading path
  exists.

## Safety boundaries

- Do not add credentials or secrets.
- Do not implement order placement.
- Do not implement WebSocket ingestion.
- Do not implement strategies in Stage 3.
- Do not enable live or production trading.
- Do not make profitability claims.
- Keep Kalshi-specific code under `src/edmn_trader/adapters/kalshi`.

## Next recommended stage

Stage 3: Local replay simulator and data recorder, built local-first with
deterministic fixtures and no execution actions.

## Exact next prompt suggestion

Implement Stage 3 for `event-driven-market-neutral-trader`: local replay
simulator and data recorder. First read `AGENTS.md`,
`docs/current_handoff.md`, `docs/repo_map.md`, and
`docs/codex_long_running_controller.md`. Start with local fixtures and
deterministic tests. Do not implement order placement, WebSocket, strategies,
credentials, production endpoints, or live trading.

## Last updated timestamp

2026-06-11 10:38:27 -07:00
