# Changelog

All notable project milestones are recorded here. This project follows the
spirit of Keep a Changelog, with stage-oriented entries instead of release
numbers while the repository is still in early research scaffolding.

## Unreleased

- Stage 3 is expected to add a local replay simulator and data recorder.
- Order placement, WebSocket ingestion, strategies, and production trading
  remain out of scope until separately reviewed.

## Stage 2 - Read-only Kalshi Demo market-data client - 2026-06-11

### Added

- Guarded `httpx`-based Kalshi Demo REST client for public read-only market
  metadata and market orderbook endpoints.
- Demo-only base URL guard using
  `https://external-api.demo.kalshi.co/trade-api/v2`.
- Local response fixtures and mocked HTTP tests for markets, orderbooks,
  normalized orderbook output, HTTP status failures, transport failures,
  malformed JSON, malformed response shapes, and empty orderbooks.

### Safety

- No credentials, authentication headers, order placement, WebSocket ingestion,
  strategy logic, production endpoint, or live trading path.

### Validation

- Required checks remain `pytest`, `ruff check .`, and
  `python scripts/01_replay_orderbook_fixture.py`.

## Stage 1.5 - Long-running controller and project memory - 2026-06-11

### Added

- Project memory and continuity docs for staged Codex work.
- Compact current handoff, repo map, long-running controller, decision log,
  staged plan, engineering narrative, and handoff archive guidance.
- Root project specification for product scope, module boundaries, non-goals,
  and acceptance standards.

### Safety

- Reaffirmed demo-first operation, no credentials, no live trading, no order
  placement, no WebSocket, and no strategy implementation in this stage.

### Validation

- Required checks remain `pytest`, `ruff check .`, and
  `python scripts/01_replay_orderbook_fixture.py`.

## Stage 1 - Kalshi-style orderbook normalization with fixtures - 2026-06-10

### Added

- Exchange-agnostic core models using `Decimal`.
- Kalshi fixed-point orderbook normalization from local fixtures.
- Deterministic tests for basic YES/NO conversion, empty sides, multiple
  levels, Decimal precision, invalid prices, and locked or crossed books.
- Local replay script for the included orderbook fixture.

### Safety

- No live API calls, authenticated requests, WebSocket ingestion, or order
  placement.

## Stage 0 - Repository foundation - 2026-06-10

### Added

- Initial Python 3.12 project structure, package metadata, test/lint setup, and
  source/test directories.
- README, AGENTS guidance, risk policy, roadmap, project charter, and resume
  narrative.
- `.env.example` with demo endpoint defaults and no secrets.

### Safety

- Rejected guaranteed-profit framing and established live trading as disabled
  by default.
