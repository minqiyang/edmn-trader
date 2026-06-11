# Codex Long-running Controller

## Objective

Keep `event-driven-market-neutral-trader` safe to continue across Codex
sessions, computers, branches, and future `/goal` runs while preserving the
demo-first, risk-controlled stage plan.

## Context-budget policy

- Read `AGENTS.md`, `docs/current_handoff.md`, and `docs/repo_map.md` first.
- Prefer targeted reads over broad file dumps.
- Use `rg` and `rg --files` for discovery.
- Read implementation files only when the requested stage needs them.
- Keep final reports concise and evidence-backed.

## Stage progression policy

- Work on one stage-sized change at a time.
- Confirm the requested stage and stop at that boundary.
- Do not begin the next stage in the same run unless explicitly requested.
- Update handoff and logs before reporting completion.

## PR-sized / commit-sized work policy

- Keep commits reviewable and scoped to the requested stage.
- Avoid unrelated refactors.
- For code changes, include tests in the same stage-sized change.
- For documentation-only stages, do not touch behavior unless required by a
  failing check.

## Stop gates

Stop and report clearly when any of these occur:

- Dirty worktree with unexpected user changes.
- Failing tests that cannot be safely fixed within scope.
- High or medium risk issue.
- Scope conflict.
- Need for credentials, secrets, production endpoint, or external trading
  access.
- Destructive command.
- Live or production trading request.
- Unclear compliance boundary.
- Completion of one stage-sized change.

## Required checks

Run these before final handoff when the environment supports them:

```bash
pytest
ruff check .
python scripts/01_replay_orderbook_fixture.py
```

For packaging or dependency changes, also run:

```bash
python -m pip install -e ".[dev]"
```

## Logging requirements

- Update `CHANGELOG.md` for stage milestones.
- Update `docs/engineering_log.md` with durable engineering narrative, not raw
  command logs.
- Update `docs/DECISION_LOG.md` when making or changing architectural or product
  decisions.

## Handoff update requirements

Before final handoff for a stage-sized change:

- Update `docs/current_handoff.md`.
- Keep it compact and current.
- Archive the previous handoff only after major stages, following
  `docs/handoff_archive/README.md`.
- Include the next recommended stage and exact next prompt suggestion.

## Final report format

Return:

- Stage completed.
- Git status.
- Branch.
- Commit hash if created.
- Files created.
- Files changed.
- Checks run and results.
- Any issues or assumptions.
- Exact recommended next prompt.

## What not to do

- Do not make profitability claims.
- Do not add credentials or secrets.
- Do not implement authenticated Kalshi requests before the read-only client
  stage is explicitly requested.
- Do not implement order placement, WebSocket ingestion, strategies, or
  production trading unless a later stage explicitly requests the appropriate
  reviewed work.
- Do not mix exchange-specific adapter code into core models.
- Do not skip tests after functional changes.
