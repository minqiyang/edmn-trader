# Repo Map

## Minimal first-pass context

Read these files before broad exploration:

1. `AGENTS.md`
2. `docs/current_handoff.md`
3. `docs/repo_map.md`

## Targeted reads only

Avoid reading the whole repository by default. Start with the minimal first-pass
context, then read only the files needed for the requested stage. Use `rg` and
`rg --files` for focused discovery.

## Root files

- `AGENTS.md`: rules for Codex sessions, safety boundaries, and required first
  reads. Read this for every task.
- `PROJECT_SPEC.md`: product and technical specification. Read when scope,
  modules, acceptance standards, or non-goals are unclear.
- `CHANGELOG.md`: external-facing milestone log. Update after stage-sized
  changes.
- `README.md`: public project overview, setup, scope, and workflow links. Read
  when changing user-facing positioning.
- `pyproject.toml`: Python package, pytest, and Ruff configuration. Read when
  changing dependencies, tooling, package layout, or entry points.
- `.env.example`: non-secret local defaults. Read when environment variables
  are relevant.

## Docs

- `docs/current_handoff.md`: compact latest state and next step. Read after
  `AGENTS.md` in future sessions.
- `docs/codex_long_running_controller.md`: staged workflow rules, stop gates,
  checks, logging, and final report format. Read before long-running stage work.
- `docs/STAGE_PLAN.md`: staged roadmap from foundation through later research
  adapters. Read when planning or validating stage boundaries.
- `docs/DECISION_LOG.md`: architecture and product decisions. Read before
  reversing or expanding a foundational decision.
- `docs/engineering_log.md`: human-readable narrative for interviews and
  project reflection. Update after stage-sized work.
- `docs/PROJECT_CHARTER.md`: mission, positioning, and initial stage boundary.
- `docs/ROADMAP.md`: compact roadmap. Use `docs/STAGE_PLAN.md` for detailed
  staged acceptance checks.
- `docs/RISK_POLICY.md`: non-negotiable safety and execution constraints.
- `docs/RESUME_NARRATIVE.md`: portfolio framing and concise project story.
- `docs/handoff_archive/README.md`: process for archiving old handoffs.

## Source

- `src/edmn_trader/core/models.py`: exchange-agnostic dataclasses and
  `ExecutionMode`. Read when changing core trading concepts.
- `src/edmn_trader/adapters/kalshi/orderbook.py`: Kalshi fixed-point
  orderbook normalizer. Read for Kalshi orderbook parsing only.
- `src/edmn_trader/scripts/replay_orderbook_fixture.py`: importable fixture
  replay entry point.
- `src/edmn_trader/**/__init__.py`: package exports.

## Scripts

- `scripts/01_replay_orderbook_fixture.py`: root-level wrapper for replaying the
  local Kalshi fixture. Run after normalization-related changes.

## Tests and fixtures

- `tests/test_core_models.py`: execution-mode and core safety checks.
- `tests/test_kalshi_orderbook.py`: deterministic normalizer coverage.
- `tests/fixtures/kalshi_orderbook_fp_basic.json`: basic local Kalshi-style
  fixture used by the replay script.

## Project Skill

- `.agents/skills/event-driven-market-neutral-trader/SKILL.md`: reusable
  project-specific Codex guidance. Read for non-trivial repo work and update
  only with verified lessons.
