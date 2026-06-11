# Engineering Log

## Why this project exists

This project exists to demonstrate professional trading-system engineering in a
portfolio-friendly way. The emphasis is not on claims of profit. The emphasis is
on correctness, staged delivery, risk boundaries, deterministic tests, and the
ability to explain how a trading research platform is built from safe
foundations.

## Why start with Kalshi-style binary orderbooks

Kalshi-style binary prediction markets are a useful first target because they
are event-driven, have a concrete demo environment, and expose an orderbook
shape that requires careful normalization. The venue returns YES bids and NO
bids, not a traditional YES bid/ask book. That forces the first implementation
to solve a real market-data modeling problem before any strategy work can begin.

## Why Stage 0 and Stage 1 focused on normalization

Stage 0 created the repository, package, safety docs, and test/lint structure.
Stage 1 added the core exchange-agnostic models and a Kalshi fixed-point
orderbook normalizer backed by local fixtures. This kept the first functional
slice deterministic and reviewable. It also avoided a common trading-system
mistake: building strategy or execution code before the market-data contract is
well understood.

The key tradeoff was intentionally narrow scope. The project did not add a REST
client, WebSocket ingestion, execution engine, optimizer, or strategy. That
slows visible feature growth, but it gives the platform a safer foundation.

## Why Stage 1.5 exists

Stage 1.5 creates the continuity layer needed for long-running Codex work. The
project is expected to continue across sessions, machines, branches, and future
goal-driven runs. Without a compact handoff, repo map, stage plan, decision log,
and controller policy, future sessions would waste context rediscovering the
same constraints or might accidentally exceed the stage boundary.

## Tradeoffs made in Stage 1.5

- Added documentation and governance files instead of new trading behavior.
- Kept `AGENTS.md` concise and moved detailed continuation policy into docs.
- Preserved the existing normalizer and tests because this stage is about
  continuity, not market-data feature work.
- Initialized Git locally because the folder was not yet a repository, but did
  not add a remote or push.

## Stage 2 read-only market-data client

Stage 2 added a narrow Kalshi Demo REST client for public market metadata and
market orderbooks. The client uses `httpx` with injectable transport so tests
can mock every HTTP response and avoid network access, credentials, and
environment assumptions. The default and only accepted base URL is the Kalshi
Demo REST base URL documented for this project.

The client deliberately exposes only read-only market and orderbook methods.
It does not include authentication, order placement, WebSocket subscriptions,
strategy hooks, or production endpoint configuration. Error handling is explicit
for HTTP status failures, transport failures, malformed JSON, malformed response
shape, and empty orderbooks.

The main tradeoff was adding a real HTTP dependency before live API use. That
is acceptable here because the dependency is exercised through mocked tests and
establishes the client seam needed for later optional live-read smoke checks.

## Interview narrative

A concise way to explain the current project:

> I built the project from the safety boundary inward. First I defined the
> non-goals and risk constraints, then I modeled a venue-agnostic orderbook and
> normalized Kalshi-style YES/NO books into a canonical bid/ask representation.
> I then added a long-running project control layer and a guarded read-only Demo
> market-data client with mocked tests, keeping execution and strategy work out
> of scope until the risk and simulation layers are ready.
