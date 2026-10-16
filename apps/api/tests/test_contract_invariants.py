import importlib.util
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import TypeAdapter, ValidationError

from app.adapters.native import NativeProvider
from app.analytics import ordered
from app.contracts import Event, NativeEvent, RuViewEvent, SensingEvent, SimulationConfig
from app.lab_contracts import ExperimentResult
from app.storage import Base, Store

ROOT = Path(__file__).resolve().parents[3]
CONTRACTS = ROOT / "packages/contracts"
EVENTS = TypeAdapter(Event)
EXAMPLES = {
    "synthetic-event.example.json": SensingEvent,
    "ruview-event.example.json": RuViewEvent,
    "native-event.example.json": NativeEvent,
}
EVENT_SCHEMAS = {
    "sensing-event.schema.json": "synthetic-event.example.json",
    "ruview-event.schema.json": "ruview-event.example.json",
    "native-event.schema.json": "native-event.example.json",
    "streaming-event.schema.json": "native-event.example.json",
}


def load(name):
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def exporter():
    spec = importlib.util.spec_from_file_location(
        "export_contract", ROOT / "scripts/verify/export_contract.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schema_valid(schema, value, root=None):
    """Tiny JSON Schema 2020-12 subset evaluator for the keywords Pydantic emits here."""
    root = root or schema
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        if not schema_valid(target, value, root):
            return False
    kinds = {
        "null": lambda v: v is None,
        "boolean": lambda v: isinstance(v, bool),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, int | float) and not isinstance(v, bool),
        "string": lambda v: isinstance(v, str),
        "array": lambda v: isinstance(v, list),
        "object": lambda v: isinstance(v, dict),
    }
    if "type" in schema and not kinds[schema["type"]](value):
        return False
    if "const" in schema and value != schema["const"]:
        return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    if kinds["number"](value):
        if "minimum" in schema and value < schema["minimum"]:
            return False
        if "maximum" in schema and value > schema["maximum"]:
            return False
    if isinstance(value, str) and "pattern" in schema:
        if not re.search(schema["pattern"], value):
            return False
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 1e9):
            return False
        prefix = schema.get("prefixItems", [])
        if not all(schema_valid(s, v, root) for s, v in zip(prefix, value, strict=False)):
            return False
        if "items" in schema and not all(
            schema_valid(schema["items"], v, root) for v in value[len(prefix) :]
        ):
            return False
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if any(key not in value for key in schema.get("required", [])):
            return False
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            return False
        if not all(
            schema_valid(properties[k], v, root) for k, v in value.items() if k in properties
        ):
            return False
    if "anyOf" in schema and not any(schema_valid(s, value, root) for s in schema["anyOf"]):
        return False
    if "oneOf" in schema and sum(schema_valid(s, value, root) for s in schema["oneOf"]) != 1:
        return False
    if "if" in schema:
        branch = schema.get("then" if schema_valid(schema["if"], value, root) else "else", {})
        if not schema_valid(branch, value, root):
            return False
    return True


def test_export_check_reports_drift_without_writing(tmp_path, capsys):
    module = exporter()
    rendered = module.render()
    assert set(rendered) >= set(EXAMPLES) | set(EVENT_SCHEMAS)
    assert module.main([], target=tmp_path) == 0
    assert module.main(["--check"], target=tmp_path) == 0
    (tmp_path / "native-event.schema.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "ruview-event.example.json").unlink()
    capsys.readouterr()
    assert module.main(["--check"], target=tmp_path) == 1
    output = capsys.readouterr().err
    assert "native-event.schema.json" in output and "ruview-event.example.json" in output
    assert "synthetic-event.example.json" not in output
    assert (tmp_path / "native-event.schema.json").read_text(encoding="utf-8") == "{}\n"
    assert not (tmp_path / "ruview-event.example.json").exists()


def test_published_contracts_match_the_python_source():
    rendered = exporter().render()
    stale = [
        name
        for name, text in rendered.items()
        if not (CONTRACTS / name).exists() or (CONTRACTS / name).read_text(encoding="utf-8") != text
    ]
    assert stale == [], "run scripts/verify/export_contract.py and review the diff"


@pytest.mark.parametrize("filename", EVENT_SCHEMAS)
def test_exported_event_schemas_encode_l0_invariants(filename):
    schema = load(filename)
    valid = load(EVENT_SCHEMAS[filename])
    assert schema_valid(schema, valid)

    def mutated(change):
        payload = json.loads(json.dumps(valid))
        change(payload)
        return schema_valid(schema, payload)

    assert not mutated(lambda p: p["quality"].update(confidence=0.9))
    assert not mutated(lambda p: p["quality"].update(signal_quality=0.5))
    assert not mutated(lambda p: p["model"].update(id="x"))
    assert not mutated(lambda p: p["model"].update(version="1"))
    assert not mutated(lambda p: p.update(evidence_level="L3_REFERENCE_VALIDATED"))
    assert not mutated(lambda p: p.update(source_type="REAL"))
    assert not mutated(lambda p: p.pop("schema_version"))
    assert not mutated(lambda p: p.pop("evidence_level"))
    assert not mutated(lambda p: p["measurements"].update(presence_detected=False))
    if valid["schema_version"] != "1.1.0":
        assert not mutated(
            lambda p: p["measurements"].update(ground_truth_positions=[[99, -5]] * 2)
        )
        assert not mutated(lambda p: p["measurements"]["ground_truth_positions"][0].append(1))


def test_streaming_schema_is_discriminated_by_schema_version():
    schema = load("streaming-event.schema.json")
    assert schema["discriminator"]["propertyName"] == "schema_version"
    assert set(schema["discriminator"]["mapping"]) == {"1.0.0", "1.1.0", "2.0.0"}
    for name in EXAMPLES:
        assert schema_valid(schema, load(name))


@pytest.mark.parametrize("name,model", EXAMPLES.items())
def test_published_examples_round_trip_through_the_union(name, model):
    payload = load(name)
    event = EVENTS.validate_python(payload)
    assert type(event) is model
    assert event.model_dump(mode="json") == payload


def test_experiment_example_matches_the_result_model():
    result = ExperimentResult.model_validate(load("experiment-result.example.json"))
    assert result.evidence_level == "L0_SYNTHETIC"


def test_identity_less_payload_is_not_relabeled_as_legacy():
    payload = load("native-event.example.json")
    for key in ("schema_version", "source_id", "event_type", "provider"):
        payload.pop(key)
    payload["provenance"].pop("generator")
    with pytest.raises(ValidationError):
        EVENTS.validate_python(payload)
    broken = load("native-event.example.json")
    broken["measurements"]["occupancy_estimate"] = -1
    with pytest.raises(ValidationError) as error:
        EVENTS.validate_python(broken)
    assert error.value.error_count() <= 2


def test_runtime_rejects_inference_quality_and_out_of_room_positions():
    valid = load("native-event.example.json")
    for change in (
        lambda p: p["quality"].update(confidence=0.9),
        lambda p: p["model"].update(id="x"),
        lambda p: p["measurements"].update(ground_truth_positions=[[99, -5]] * 2),
        lambda p: p["measurements"].update(ground_truth_positions=[[8.5, 1]] * 2),
    ):
        payload = json.loads(json.dumps(valid))
        change(payload)
        with pytest.raises(ValidationError):
            EVENTS.validate_python(payload)


@pytest.mark.parametrize(
    "change",
    [
        {"scenario": "custom"},
        {"dataset_id": "ds-1"},
        {"seed": -1},
        {"seed": 2**32},
        {"seed": 2**60},
    ],
)
def test_native_provenance_matches_the_dashboard_contract(change):
    payload = load("native-event.example.json")
    payload["provenance"].update(change)
    with pytest.raises(ValidationError):
        EVENTS.validate_python(payload)


def test_legacy_events_keep_their_historical_tolerance():
    payload = load("synthetic-event.example.json")
    payload["event_id"] = str(UUID(int=1))
    payload["provenance"].update(scenario="custom", dataset_id="ds-1", seed=2**60)
    assert type(EVENTS.validate_python(payload)) is SensingEvent


@pytest.mark.parametrize(
    "scenario",
    [
        "empty",
        "stationary",
        "walking",
        "entering",
        "leaving",
        "interference",
        "packet_loss",
        "disconnect",
    ],
)
def test_native_producer_satisfies_the_tightened_contract(scenario):
    config = SimulationConfig(scenario=scenario, seed=2**32 - 1, occupants=20)
    provider = NativeProvider(config)
    for _ in range(12):
        event = provider.sample(datetime(2026, 1, 1, tzinfo=UTC))
        if event is not None:
            assert type(EVENTS.validate_json(event.model_dump_json())) is NativeEvent


def test_stored_payloads_of_every_version_are_read_back(tmp_path):
    store = Store(f"sqlite:///{tmp_path / 'contracts.db'}", retention=100)
    Base.metadata.create_all(store.engine)
    for name in EXAMPLES:
        assert store.write(EVENTS.validate_python(load(name)))
    items = store.history(10, 0)["items"]
    assert sorted(item["schema_version"] for item in items) == ["1.0.0", "1.1.0", "2.0.0"]
    events = ordered([{"event": item, "segment_id": None} for item in items])
    assert {type(event) for event, _ in events} == set(EXAMPLES.values())
