# Project Charter

## Mission

Build a demo-first, risk-controlled trading research platform for event-driven
prediction markets, starting with Kalshi-style binary contracts and designed to
extend later toward broader market-neutral automated trading research.

## Positioning

This repository demonstrates professional trading-system design for a resume
and GitHub portfolio. It is a research, simulation, execution-safety, and
workflow-engineering project. It is not a guaranteed-profit trading bot.

## Design principles

- Demo and paper workflows come before execution.
- Production trading is disabled by default.
- Credentials and secrets do not belong in the repository.
- The risk engine must exist before any execution engine.
- Deterministic tests come before live API behavior.
- Prices, quantities, fees, cash, and PnL use `Decimal`.
- Exchange-specific code stays in adapters.
- Core trading models remain exchange-agnostic.
- Strategy outputs must pass risk checks before execution in future stages.
- Execution actions must be logged in future execution stages.

## Initial integration target

Kalshi Demo is the first external target.

```text
REST: https://external-api.demo.kalshi.co/trade-api/v2
WebSocket, later stage only: wss://external-api-ws.demo.kalshi.co/trade-api/ws/v2
```

Stage 0 and the first Stage 1 implementation use local fixtures only.

## Stage boundary

The current foundation stops at core models and Kalshi orderbook normalization.
It does not implement authenticated requests, WebSocket ingestion, order
placement, strategy optimization, or production trading.
