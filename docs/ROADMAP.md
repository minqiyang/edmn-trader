# Roadmap

## Stage 0: Repository foundation

- Create project documentation, package configuration, lint/test setup, and
  source/test structure.
- Define the demo-first safety boundary.
- Document why profitability guarantees are rejected.

## Stage 1: Local orderbook normalization

- Define exchange-agnostic core models.
- Normalize Kalshi-style YES/NO orderbooks into canonical YES-side bid/ask
  books using local fixtures.
- Test empty sides, multiple levels, precision, invalid prices, and locked or
  crossed books.

## Stage 2: Read-only Kalshi Demo market data

- Add unauthenticated or appropriately configured demo REST clients only after
  tests cover parsing behavior with local fixtures.
- Keep credentials outside the repository.
- Add rate-limit and failure-mode handling before any repeated polling workflow.

## Stage 3: Simulation and PnL accounting

- Add maker/taker simulation with explicit fill assumptions.
- Track positions, cash, fees, realized and unrealized PnL, spread capture, and
  adverse-selection proxies.
- Document limitations for every simulation report.

## Stage 4: Risk engine and paper execution workflow

- Implement pre-trade risk checks before any execution pathway.
- Keep live execution disabled.
- Log every paper/demo execution action.

## Stage 5: Additional research adapters

- Add Polymarket US market-data research support without implementing
  Polymarket trading.
- Add U.S. equities research data support without implementing live equities
  trading.
- Preserve the adapter boundary so the core workflow does not depend on one
  venue.
