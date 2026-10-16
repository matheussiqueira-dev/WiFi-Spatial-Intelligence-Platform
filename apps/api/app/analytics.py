"""Deterministic analytics over persisted synthetic observations, never identity tracking."""

import csv
import io
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from pydantic import Field, TypeAdapter, ValidationError, model_validator

from app.contracts import Event, StrictModel

adapter = TypeAdapter(Event)
logger = logging.getLogger("spatial.analytics")


class AnalyticsQuery(StrictModel):
    start: datetime
    end: datetime
    bucket: Literal["minute", "five_minutes", "hour", "day"] = "minute"
    room_id: Literal["living-room"] = "living-room"
    source_id: Literal["native-01", "simulator-01", "ruview-01"] | None = None
    scenario: str | None = Field(default=None, max_length=40, pattern=r"^[a-z_-]+$")
    segment_id: str | None = Field(default=None, pattern=r"^[a-f0-9-]{36}$")
    gap_seconds: float = Field(default=5, ge=1, le=60)
    limit: int = Field(default=100, ge=1, le=200)
    offset: int = Field(default=0, ge=0, le=10000)

    @model_validator(mode="after")
    def bounded_utc(self):
        for value in (self.start, self.end):
            if (offset := value.utcoffset()) is None or offset.total_seconds() != 0:
                raise ValueError("start/end must be timezone-aware UTC")
        if not timedelta(0) < self.end - self.start <= timedelta(days=31):
            raise ValueError("range must be positive and at most 31 days")
        if self.end > datetime.now(UTC) + timedelta(seconds=2):
            raise ValueError("future range is not allowed")
        return self


def validated_rows(rows):
    """Valid (event, segment) pairs in order plus the count of stored payloads rejected."""
    validated = []
    seen = set()
    invalid = 0
    for row in rows:
        try:
            event = adapter.validate_python(row["event"])
        except (ValidationError, KeyError, TypeError):
            invalid += 1
            continue
        if event.event_id not in seen:
            validated.append((event, row["segment_id"]))
            seen.add(event.event_id)
    if invalid:
        # Count only: stored payloads must not be copied into the logs.
        logger.warning("analytics.invalid_stored_records count=%d", invalid)
    pairs = sorted(validated, key=lambda pair: (pair[0].timestamp, str(pair[0].event_id)))
    return pairs, invalid


def ordered(rows):
    return validated_rows(rows)[0]


def replay_page(rows, total, query):
    """A page already ordered and limited in SQL; corrupt payloads are skipped and logged."""
    events, _ = validated_rows(rows)
    return {
        "evidence_level": "L0_SYNTHETIC",
        "mode": "REPLAY",
        "snapshot_end": query.end.isoformat(),
        "items": [
            {"event": event.model_dump(mode="json"), "segment_id": segment}
            for event, segment in events
        ],
        "total": total,
        "limit": query.limit,
        "offset": query.offset,
    }


def page(items, query):
    return {
        "items": items[query.offset : query.offset + query.limit],
        "total": len(items),
        "limit": query.limit,
        "offset": query.offset,
    }


def replay(rows, query):
    # Order and deduplicate on the stored keys; full validation only for the requested page.
    unique = {}
    for row in rows:
        identifier = str(row["event"]["event_id"])
        if identifier not in unique:
            timestamp = datetime.fromisoformat(row["event"]["timestamp"])
            unique[identifier] = (timestamp, identifier, row)
    selection = sorted(unique.values(), key=lambda item: item[:2])
    window = selection[query.offset : query.offset + query.limit]
    items = []
    for _, _, row in window:
        event = adapter.validate_python(row["event"])
        items.append({"event": event.model_dump(mode="json"), "segment_id": row["segment_id"]})
    return {
        "evidence_level": "L0_SYNTHETIC",
        "mode": "REPLAY",
        "snapshot_end": query.end.isoformat(),
        "items": items,
        "total": len(selection),
        "limit": query.limit,
        "offset": query.offset,
    }


def aggregate(rows, query):
    events, invalid = validated_rows(rows)
    seconds = {"minute": 60, "five_minutes": 300, "hour": 3600, "day": 86400}[query.bucket]
    buckets: dict[tuple[int, str], dict] = {}
    previous: dict[tuple[str, str], Any] = {}
    intervals = []
    transitions = []
    latencies = []
    segments = set()
    excluded_transitions = 0
    for event, segment in events:
        timestamp = event.timestamp
        # Legacy events have no recorded session. Never infer continuity for them.
        group = (event.source_id, segment or str(event.event_id))
        segments.add((event.source_id, segment))
        key = (int(timestamp.timestamp()) // seconds * seconds, event.source_id)
        bucket = buckets.setdefault(
            key,
            {
                "timestamp": datetime.fromtimestamp(key[0], UTC).isoformat(),
                "source_id": event.source_id,
                "samples": 0,
                "presence_samples": 0,
                "known_count_samples": 0,
                "unknown_count_samples": 0,
                "occupancy_sum": 0,
                "occupancy_max": None,
                "entries_estimate": 0,
                "exits_estimate": 0,
                "evidence_level": "L0_SYNTHETIC",
            },
        )
        bucket["samples"] += 1
        bucket["presence_samples"] += int(event.measurements.presence_detected)
        count = event.measurements.occupancy_estimate
        if count is None:
            bucket["unknown_count_samples"] += 1
        else:
            bucket["known_count_samples"] += 1
            bucket["occupancy_sum"] += count
            bucket["occupancy_max"] = max(bucket["occupancy_max"] or 0, count)
        if event.processing_latency_ms is not None:
            latencies.append(event.processing_latency_ms)
        prior = previous.get(group)
        if prior:
            old = prior
            gap = (timestamp - old.timestamp).total_seconds()
            continuous = (
                0 < gap <= query.gap_seconds
                and event.provenance.tick > old.provenance.tick
                and event.provenance.scenario == old.provenance.scenario
            )
            state = "present" if old.measurements.presence_detected else "absent"
            intervals.append(
                {
                    "start": old.timestamp.isoformat(),
                    "end": timestamp.isoformat(),
                    "source_id": event.source_id,
                    "segment_id": segment,
                    "state": state if continuous else "unknown",
                    "duration_seconds": gap,
                    "evidence_level": "L0_SYNTHETIC",
                }
            )
            old_count = old.measurements.occupancy_estimate
            if continuous and old_count is not None and count is not None:
                delta = count - old_count
                if (
                    delta
                    or old.measurements.presence_detected != event.measurements.presence_detected
                ):
                    transitions.append(
                        {
                            "timestamp": timestamp.isoformat(),
                            "event_id": str(event.event_id),
                            "source_id": event.source_id,
                            "segment_id": segment,
                            "from_count": old_count,
                            "to_count": count,
                            "entries_estimate": max(0, delta),
                            "exits_estimate": max(0, -delta),
                            "evidence_level": "L0_SYNTHETIC",
                        }
                    )
                    bucket["entries_estimate"] += max(0, delta)
                    bucket["exits_estimate"] += max(0, -delta)
            else:
                excluded_transitions += 1
        previous[group] = event
    result = []
    for _, bucket in sorted(buckets.items()):
        count = bucket.pop("occupancy_sum")
        known = bucket["known_count_samples"]
        bucket["occupancy_mean"] = count / known if known else None
        bucket["presence_fraction"] = bucket["presence_samples"] / bucket["samples"]
        result.append(bucket)
    latencies.sort()
    duration = (events[-1][0].timestamp - events[0][0].timestamp).total_seconds() if events else 0
    return {
        "schema_version": "1.0.0",
        "evidence_level": "L0_SYNTHETIC",
        "validation_status": "IMPLEMENTED_SYNTHETIC",
        "mode": "HISTORICAL",
        "query": query.model_dump(mode="json"),
        "summary": {
            "samples": len(events),
            "segments": len(segments),
            "entries_estimate": sum(item["entries_estimate"] for item in result),
            "exits_estimate": sum(item["exits_estimate"] for item in result),
            "unknown_count_samples": sum(item["unknown_count_samples"] for item in result),
            "presence_seconds": sum(
                i["duration_seconds"] for i in intervals if i["state"] == "present"
            ),
            "absent_seconds": sum(
                i["duration_seconds"] for i in intervals if i["state"] == "absent"
            ),
            "unknown_seconds": sum(
                i["duration_seconds"] for i in intervals if i["state"] == "unknown"
            ),
            "excluded_transitions": excluded_transitions,
            "event_rate": len(events) / duration if duration > 0 else None,
            "queue_wait_p50_ms": latencies[int((len(latencies) - 1) * 0.5)] if latencies else None,
            "queue_wait_p95_ms": latencies[int((len(latencies) - 1) * 0.95)] if latencies else None,
            "rf_drop_rate": None,
        },
        "buckets": page(result, query),
        "intervals": page(intervals, query),
        "transitions": page(transitions, query),
        "limitations": [
            "Sample-weighted counts; not time-weighted occupancy or validated inference.",
            "Count deltas are net estimates, not individual door crossings or identities.",
            "Gaps, unknown counts, segment boundaries and nonincreasing ticks break transitions.",
            "Legacy records lack session attribution; no transitions inferred for them.",
            "No extrapolation before first/after last sample; missing buckets are unknown.",
            "Queue wait measures time before persistence, not sensing or total processing latency.",
        ]
        + (
            [
                f"{invalid} stored record(s) failed contract validation and were excluded; "
                "run an integrity check before relying on this period."
            ]
            if invalid
            else []
        ),
    }


def csv_report(report):
    output = io.StringIO(newline="")
    fields = [
        "timestamp",
        "source_id",
        "samples",
        "occupancy_mean",
        "occupancy_max",
        "presence_fraction",
        "unknown_count_samples",
        "entries_estimate",
        "exits_estimate",
        "evidence_level",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for bucket in report["buckets"]["items"]:
        writer.writerow(
            {
                key: (
                    "'" + str(value)
                    if isinstance(value, str) and value.startswith(("=", "+", "-", "@"))
                    else value
                )
                for key, value in bucket.items()
            }
        )
    return output.getvalue()
