#!/usr/bin/env python3
"""Export packages/contracts from the Python models; --check compares without writing."""

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "apps/api"))
from app.adapters.native import NativeProvider
from app.analytics import AnalyticsQuery, aggregate, replay
from app.application.model_lab import ExperimentRequest
from app.capabilities import CapabilityCatalog, catalog
from app.contracts import (
    Event,
    NativeEvent,
    RuViewEvent,
    RuViewMeasurements,
    RuViewProvenance,
    SensingEvent,
    SimulationConfig,
)
from app.domain.motion import evaluate_baseline, prepare_dataset
from app.lab_contracts import ExperimentResult
from app.network_contracts import (
    ChannelPlan,
    ChannelSurvey,
    NetworkReport,
    NetworkSample,
)
from app.simulator import SimulationProvider
from pydantic import TypeAdapter

TARGET = root / "packages/contracts"
START = datetime(2026, 1, 1, tzinfo=UTC)
SEGMENT = "00000000-0000-4000-8000-00000000a001"
events = TypeAdapter(Event)


def dump(payload):
    return json.dumps(payload, indent=2) + "\n"


def emitted(schema_source):
    # Event schemas describe emitted payloads, where every defaulted field is present.
    return schema_source.json_schema(mode="serialization")


def golden_rows(legacy, ruview):
    """Native session with entries, a gap, plus legacy and unknown-count RuView rows."""
    provider = NativeProvider(SimulationConfig(scenario="entering"))
    rows = [{"event": legacy, "segment_id": None}]
    for tick in range(8):
        offset = (
            tick if tick < 7 else 30
        )  # Longer than gap_seconds: interval becomes unknown.
        event = provider.sample(START + timedelta(seconds=offset)).model_dump(
            mode="json"
        )
        event["event_id"] = f"00000000-0000-4000-8000-{0x100 + tick:012x}"
        rows.append({"event": event, "segment_id": SEGMENT})
    unknown = {**ruview, "event_id": "00000000-0000-4000-8000-000000000201"}
    unknown["timestamp"] = "2026-01-01T00:00:10Z"
    unknown["measurements"] = {**ruview["measurements"], "occupancy_estimate": None}
    rows.append({"event": unknown, "segment_id": SEGMENT})
    for row in rows:
        events.validate_python(row["event"])
    return rows


def render():
    sample = SimulationProvider(SimulationConfig()).sample(START)
    data = sample.model_dump(mode="json")
    data["event_id"] = "00000000-0000-4000-8000-000000000001"
    ruview_sample = RuViewEvent(
        event_id="00000000-0000-4000-8000-000000000002",
        timestamp=START,
        measurements=RuViewMeasurements(presence_detected=True, occupancy_estimate=1),
        provenance=RuViewProvenance(tick=113),
    ).model_dump(mode="json")
    native = NativeProvider(SimulationConfig()).sample(START).model_dump(mode="json")
    native["event_id"] = "00000000-0000-4000-8000-000000000003"
    for payload in (data, ruview_sample, native):
        events.validate_python(payload)
    query = AnalyticsQuery(start=START, end=START + timedelta(days=1))
    experiment = {
        **evaluate_baseline(prepare_dataset(42)),
        "id": "00000000-0000-4000-8000-000000000004",
        "created_at": "2026-01-01T00:00:00Z",
        "seed": 42,
        "duration_ms": 0.0,
    }
    ExperimentResult.model_validate(experiment)
    rows = golden_rows(data, ruview_sample)
    return {
        "sensing-event.schema.json": dump(emitted(TypeAdapter(SensingEvent))),
        "synthetic-event.example.json": dump(data),
        "ruview-event.schema.json": dump(emitted(TypeAdapter(RuViewEvent))),
        "streaming-event.schema.json": dump(emitted(events)),
        "ruview-event.example.json": dump(ruview_sample),
        "analytics-query.schema.json": dump(AnalyticsQuery.model_json_schema()),
        "analytics-report.example.json": dump(
            aggregate([{"event": data, "segment_id": None}], query)
        ),
        "analytics-native-report.example.json": dump(aggregate(rows, query)),
        "analytics-replay.example.json": dump(replay(rows, query)),
        "native-event.schema.json": dump(emitted(TypeAdapter(NativeEvent))),
        "native-event.example.json": dump(native),
        "experiment-request.schema.json": dump(ExperimentRequest.model_json_schema()),
        "experiment-result.schema.json": dump(ExperimentResult.model_json_schema()),
        "experiment-result.example.json": dump(experiment),
        "network-sample.schema.json": dump(NetworkSample.model_json_schema()),
        "network-report.schema.json": dump(NetworkReport.model_json_schema()),
        "channel-survey.schema.json": dump(ChannelSurvey.model_json_schema()),
        "channel-plan.schema.json": dump(ChannelPlan.model_json_schema()),
        "capability-catalog.schema.json": dump(CapabilityCatalog.model_json_schema()),
        "capability-catalog.example.json": dump(catalog("lab").model_dump(mode="json")),
    }


def main(argv=None, target=TARGET):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="exit 1 listing stale files; never writes"
    )
    args = parser.parse_args(argv)
    rendered = render()
    if args.check:
        # Universal newlines: a CRLF checkout of identical JSON is not drift.
        stale = [
            name
            for name, text in rendered.items()
            if not (target / name).is_file()
            or (target / name).read_text(encoding="utf-8") != text
        ]
        for name in stale:
            print(f"stale contract: {name}", file=sys.stderr)
        if stale:
            print(
                "Run scripts/verify/export_contract.py and review the diff.",
                file=sys.stderr,
            )
            return 1
        print(f"Contracts in sync ({len(rendered)} files).")
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for name, text in rendered.items():
        (target / name).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
