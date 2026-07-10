# Kalshi WebSocket Raw Event Schema v2

## Scope

D2A records each parsed Kalshi Demo WebSocket message as a versioned native
evidence envelope. It preserves transport evidence and decides whether an
orderbook message is eligible for a future rebuild. It does not rebuild a
book, subscribe to additional channels, classify a campaign, or enable paper,
Demo order, production, or real-money behavior.

The schema identifier is `edmn.kalshi.ws.raw.v2`.

## Envelope fields

Native values are copied without using local append order as a substitute:

- `native_type`
- `native_sid`
- `native_seq`
- `native_market_ticker`
- `native_market_id`
- `native_exchange_ts`
- `native_exchange_ts_ms`
- `original_payload`

Recorder-owned transport context is separate:

- `local_row_index`: one-based append order in the current raw file
- `connection_id`: recorder-assigned connection attempt identity
- `segment_id` and `segment_boundary_reason`: integrity segment identity
- `received_at_utc` and `received_monotonic_ns`: local receipt clocks
- `channel`
- `subscription_id`, `subscription_sid`, and `subscription_command_id`
- `admission_status`, `exclusion_reason`, `sequence_continuity_policy`,
  `sequence_state`, and `resync_state`
- `campaign_id`, `requested_market_tickers`, `record_type`, and `venue`
- `payload_sha256`

Unknown native fields remain under `original_payload`. Secret-like keys,
including authentication headers, signatures, API keys, tokens, and private
key material, are rejected before an envelope can be constructed. Non-object
WebSocket JSON is rejected rather than wrapped as a native object.

## Payload hash

`payload_sha256` hashes the exact parsed native payload represented by
`original_payload`, not the envelope or the whole JSONL file. The deterministic
byte representation is UTF-8 JSON produced with sorted object keys, compact
separators, Unicode preserved, and non-finite numbers rejected:

```python
json.dumps(
    original_payload,
    ensure_ascii=False,
    allow_nan=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

This makes semantically identical parsed objects hash identically even when
their object-key insertion order differs. It does not claim to preserve the
original WebSocket frame's whitespace or wire encoding.

Exact serialized-record chaining and closed-file hashing remain D2D work and
are not evidence provided by `payload_sha256`.

## Sequence semantics

The default continuity policy is `UNKNOWN`. Numeric monotonicity is therefore
observational only:

- absent `seq` -> `SEQUENCE_NOT_OBSERVED`
- first or non-integer `seq` with unknown semantics ->
  `SEQUENCE_PRESENT_SEMANTICS_UNKNOWN`
- later increasing integer under unknown semantics ->
  `SEQUENCE_OBSERVED_MONOTONIC`
- duplicate or decreasing integer in one segment -> conservative typed
  exclusion and resync, without asserting documented exchange continuity
- numeric jump under unknown semantics -> monotonic observation, not a gap
- exact `+1` continuity or a numeric gap is asserted only under the explicit
  `CONTIGUOUS_INCREMENT` policy used by controlled fixtures

No sequence state crosses a SID, connection, subscription, or segment
boundary. In particular, monotonic observations do not imply a sequence
integrity pass.

## Segments and admission

Connections, reconnections, first subscriptions, resubscriptions, SID changes,
and supported-policy integrity failures advance the segment identity. A
connection boundary followed immediately by a subscription boundary may
advance the internal segment counter twice before the first row is emitted;
only segments containing received rows appear in JSONL.

Every orderbook segment begins with `RESYNC_REQUIRED` and no accepted snapshot
for any requested market. An `orderbook_snapshot` initializes its market within
that segment and changes that market's event state to
`RESYNCED_WITH_SNAPSHOT`. A delta for any other requested market remains
preserved raw but is `EXCLUDED` with `DELTA_BEFORE_SNAPSHOT` until that market
has its own snapshot. Missing or unrequested market tickers are also excluded.

A supported-policy gap, duplicate, or out-of-order observation is preserved,
excluded, and marks resynchronization required. The following segment accepts
no deltas until a fresh snapshot arrives. That snapshot starts new admitted
history; it does not repair missing history in the prior segment.

## Legacy compatibility

Unversioned recorder rows use a dedicated `LegacyKalshiWsRawEvent` view. Their
old top-level `sequence` becomes `local_row_index` only. It is never promoted
to `native_seq`, even if the nested legacy payload happens to contain a native
`seq`. Such rows are marked `LEGACY_LOCAL_SEQUENCE_ONLY` and are ineligible as
native sequence evidence. Unknown explicit schema versions fail with a typed
compatibility error.

## Evidence boundary

D2A does not implement native orderbook rebuild or replay qualification. The
existing campaign summary `gap_count=0` remains a legacy, unmeasured value and
must not be interpreted as verified sequence integrity. D2B requires separate
authorization to consume admitted snapshot/delta segments and implement venue
semantics. Public live execution remains disabled, and real-money trading is a
strict no-go.
