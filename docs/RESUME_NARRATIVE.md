# Resume Narrative

## Project summary

Built a demo-first, risk-controlled trading research platform for event-driven
prediction markets, starting with Kalshi-style binary orderbook normalization
and designed for future simulation, risk checks, and paper execution workflows.

## Engineering themes

- Exchange-agnostic core models separated from venue-specific adapters.
- `Decimal`-based price and quantity handling for financial correctness.
- Deterministic local-fixture tests before any live API behavior.
- Explicit risk policy that disables production trading by default.
- Documentation that frames the project as research infrastructure rather than
  a profitability promise.

## Current technical artifact

The first implementation converts Kalshi-style YES bid and NO bid books into a
canonical YES-side bid/ask book. This enables later fair-value estimation,
inventory-aware quoting, simulation, and risk checks to consume one normalized
market-data shape regardless of venue-specific input format.

## Future portfolio value

Later stages can demonstrate market-data ingestion, simulation accounting,
risk-decision workflows, and adapter extensibility for additional prediction
market and equities research data sources while preserving demo-first execution
safety.
