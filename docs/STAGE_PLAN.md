# Stage Plan

## Stage 0: Repository foundation

Purpose: establish the package, public positioning, tooling, and safety
boundary.

Deliverables: README, AGENTS guidance, package structure, pytest/Ruff setup,
risk policy, charter, roadmap, and resume narrative.

Acceptance checks: editable install works, `pytest` passes, `ruff check .`
passes, and no credentials or live trading paths exist.

Explicit non-goals: no API clients, no execution, no strategies, no WebSocket,
and no profitability claims.

## Stage 1: Kalshi-style orderbook normalization with fixtures

Purpose: normalize Kalshi-style YES/NO books into canonical YES-side bid/ask
books.

Deliverables: exchange-agnostic core models, Kalshi normalizer, local fixture,
replay script, and deterministic tests.

Acceptance checks: tests cover basic conversion, empty sides, multiple levels,
precision, invalid prices, and locked or crossed books.

Explicit non-goals: no live API calls, no authenticated requests, no order
placement, no WebSocket, and no strategy logic.

## Stage 1.5: Long-running controller and project memory

Purpose: make the repository safe to continue across sessions, branches,
computers, and future `/goal` runs.

Deliverables: changelog, project spec, current handoff, engineering log, repo
map, long-running controller, stage plan, decision log, handoff archive
guidance, and concise AGENTS/README references.

Acceptance checks: required docs exist, `pytest` passes, `ruff check .` passes,
fixture replay works, and Git is initialized on `main` if it was absent.

Explicit non-goals: no REST client, no order placement, no WebSocket, no
strategies, and no normalizer changes except minimal check fixes.

## Stage 2: Read-only Kalshi Demo market-data client

Purpose: add a safe read-only client boundary for Kalshi Demo market data.

Deliverables: local response fixtures, parsing tests, read-only client module,
configuration for demo base URL, error handling, and no secret storage.

Acceptance checks: tests pass without network or credentials, live network use
is optional or explicitly separated, and rate-limit/failure behavior is
documented.

Explicit non-goals: no authenticated trading, no order placement, no WebSocket,
no strategies, and no production endpoints.

## Stage 3: Local replay simulator and data recorder

Purpose: simulate market-data replay and prepare local data capture workflows
for research.

Deliverables: replay loop, recorder interface, local storage format, fixture
coverage, and limitation notes.

Acceptance checks: deterministic replay tests pass, data output format is
documented, and no execution actions are possible.

Explicit non-goals: no live trading, no strategy optimization, no hidden network
dependencies, and no unsupported data redistribution.

## Stage 4: Fair-value and quote engine dry-run

Purpose: estimate fair value and generate inventory-aware dry-run quotes.

Deliverables: fair-value interface, quote engine, quote tests, and dry-run
reports with assumptions.

Acceptance checks: strategy outputs remain dry-run objects, all prices and
quantities use `Decimal`, and limitations are documented.

Explicit non-goals: no order placement, no live execution, no profitability
claims, and no optimizer that implies guaranteed performance.

## Stage 5: Risk-gated demo execution smoke test

Purpose: prove that demo execution actions cannot occur without explicit risk
approval and logging.

Deliverables: risk checks, execution log format, demo-only smoke test path, and
blocked-path tests.

Acceptance checks: every execution action passes risk checks, `LIVE_DISABLED`
cannot place orders, logs are auditable, and tests cover rejection paths.

Explicit non-goals: no production trading, no broad strategy deployment, no
credential storage, and no compliance bypass.

## Stage 6: Inventory-aware demo market maker in dry-run/demo only

Purpose: connect normalized books, fair value, quote generation, risk checks,
and demo/paper execution in a controlled workflow.

Deliverables: inventory-aware quote adjustments, dry-run/demo loop, risk gates,
structured logs, and run summaries.

Acceptance checks: dry-run works without credentials, demo mode is explicitly
configured, risk checks gate all actions, and limitations are reported.

Explicit non-goals: no production deployment, no aggressive liquidity behavior,
no spoofing-like behavior, and no performance guarantees.

## Stage 7: PnL attribution and research report

Purpose: explain simulated or demo results with fees, fills, spread capture,
inventory, and adverse-selection proxies.

Deliverables: attribution model, report template, charts or tables, and
assumption disclosures.

Acceptance checks: reports separate observed results from assumptions, include
fees/slippage/fill limitations, and avoid profitability guarantees.

Explicit non-goals: no marketing claims, no cherry-picked conclusions, and no
production trading.

## Stage 8: Polymarket US market-data research adapter, if compliant and available

Purpose: explore a second prediction-market data adapter for research only.

Deliverables: compliance review note, market-data adapter, fixtures, parser
tests, and docs on availability and limitations.

Acceptance checks: no trading path exists, adapter stays separate from core, and
use is compliant with availability and platform rules.

Explicit non-goals: no Polymarket trading, no bypassing restrictions, no wallet
integration, and no production execution.

## Stage 9: U.S. equities research adapter, paper/research only

Purpose: extend the research architecture toward equities data without enabling
live equities trading.

Deliverables: equities research adapter, local fixtures, parser tests, and
paper/research documentation.

Acceptance checks: no live execution path exists, data assumptions are
documented, and core workflow remains exchange-agnostic.

Explicit non-goals: no live equities orders, no broker integration for
production trading, no credentials in repo, and no claims of guaranteed
performance.
