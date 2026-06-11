"""Decimal-safe JSON Lines helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class JSONLDecodeError(ValueError):
    """Raised when a JSONL file contains malformed JSON or non-object records."""

    def __init__(self, path: Path, line_number: int, reason: str) -> None:
        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"{path}:{line_number}: {reason}")


def read_jsonl_records(path: Path) -> Iterator[dict[str, Any]]:
    """Yield object records from a JSONL file."""

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise JSONLDecodeError(path, line_number, "malformed JSON") from exc

            if not isinstance(record, dict):
                raise JSONLDecodeError(path, line_number, "JSONL record must be an object")

            yield record


def write_jsonl_records(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Write JSONL records, replacing any existing file."""

    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(_to_json_line(record))


def append_jsonl_record(path: Path, record: Mapping[str, Any]) -> None:
    """Append one JSONL record."""

    append_jsonl_records(path, [record])


def append_jsonl_records(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Append JSONL records, creating the file and parent directories if needed."""

    _ensure_parent(path)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(_to_json_line(record))


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _to_json_line(record: Mapping[str, Any]) -> str:
    json_ready = _to_json_value(record)
    return f"{json.dumps(json_ready, sort_keys=True, separators=(',', ':'))}\n"


def _to_json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _to_json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_to_json_value(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        return _to_json_value(asdict(value))
    return value
