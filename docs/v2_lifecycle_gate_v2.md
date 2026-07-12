# V2 Lifecycle Gate

The seven-day read-only recorder uses a conservative lifecycle deadline rather
than `close_time` alone.

```text
campaign_required_end = selected_at_utc + duration_seconds + safety_buffer_seconds
lifecycle_deadline = min(close_time, expected_expiration_time,
                         occurrence_datetime, explicit_early_close_deadline,
                         settlement_time)
```

`latest_expiration_time` is retained as metadata but is never the sole safety
deadline. A market must be `open` or `trading`, and every applicable
conservative deadline must exceed `campaign_required_end`.

`occurrence_datetime` remains a conservative deadline because its current
contract is unresolved. Kalshi's changelog defines it as the recorded time when
the underlying event occurred, when available, but independent Demo
revalidation returned a future value equal to `close_time` and
`expected_expiration_time`. Until Kalshi clarifies that contradiction, the gate
fails closed and does not interpret the field as purely retrospective.
`close_time` can move earlier when `can_close_early=true`, while
`expected_expiration_time` is the forecast time when the outcome should be
known. See Kalshi's
[market lifecycle](https://docs.kalshi.com/getting_started/market_lifecycle) and
[April 16, 2026 changelog](https://docs.kalshi.com/changelog).

The long-horizon gate rejects early-close markets without expected-expiration
or explicit early-close deadline metadata, early expected expiration or
occurrence, missing event metadata, and sports/match markets unless an explicit
future configuration allows that category. The manifest preserves the raw
lifecycle fields, normalized status, event metadata, lifecycle deadline,
required end, and structured rejection reason.

Selection is explicit across three profiles. Smoke uses a 900-second buffer.
The 1,800-second canary uses a 3,600-second buffer, requires complete event
category/title metadata from the core event endpoint, rejects sports and
match-like events, and rejects any
`can_close_early=true` candidate. Seven-day selection uses at least an
86,400-second buffer and retains the stricter long-horizon rules. The manifest
records the selected profile and buffer. None of these profiles implies
seven-day evidence before the corresponding bounded run completes.

Discovery fetches at most 100 market pages before event hydration, deduplicates
markets and event tickers, hydrates core events in bounded batches, and caches
them for the run. `coverage_complete=true` requires the final market cursor to
be empty. Reaching the page cap with a cursor remaining returns
`DEMO_MARKET_DISCOVERY_INCOMPLETE_PAGE_LIMIT` and cannot authorize a candidate.
Missing batch members may use a candidate-local single-event fallback. Rate
limits and transient server/transport failures receive at most three attempts;
an exhausted request marks coverage incomplete rather than claiming that no
eligible market exists. Complete results include a versioned profile hash,
primary and multi-label rejection totals, distinct/duplicate counts, and up to
100 hashed near-miss summaries without raw market payloads.

Validation reports separate `DATA_INTEGRITY_PASS` from
`CAMPAIGN_EVIDENCE_INVALID_MARKET_LIFECYCLE`; clean JSONL/hash/artifact
integrity cannot turn a closed or resolved market into valid long-horizon
evidence. The public live gate remains disabled and no order-write path is
introduced.
