# V2 Lifecycle Gate

The seven-day read-only recorder uses a conservative lifecycle deadline rather
than `close_time` alone.

```text
campaign_required_end = selected_at_utc + duration_seconds + safety_buffer_seconds
lifecycle_deadline = min(close_time, expected_expiration_time,
                         occurrence_datetime, explicit_early_close_deadline)
```

`latest_expiration_time` is retained as metadata but is never the sole safety
deadline. A market must be `open` or `trading`, and every applicable
conservative deadline must exceed `campaign_required_end`.

The long-horizon gate rejects early-close markets without expected-expiration
or explicit early-close deadline metadata, early expected expiration or event
occurrence, missing event metadata, and sports/match markets unless an explicit
future configuration allows that category. The manifest preserves the raw
lifecycle fields, normalized status, event metadata, lifecycle deadline,
required end, and structured rejection reason.

Five-minute smoke and 30-minute canary profiles remain bounded duration
profiles with their own safety buffer. They do not imply seven-day evidence.

Validation reports separate `DATA_INTEGRITY_PASS` from
`CAMPAIGN_EVIDENCE_INVALID_MARKET_LIFECYCLE`; clean JSONL/hash/artifact
integrity cannot turn a closed or resolved market into valid long-horizon
evidence. The public live gate remains disabled and no order-write path is
introduced.
