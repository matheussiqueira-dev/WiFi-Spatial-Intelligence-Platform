import json
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.application.rf_fingerprint_lab import evaluate
from app.domain.rf_fingerprint import (
    MIN_FRAMES,
    WINDOW,
    Change,
    assess,
    build,
    calibrate,
    distance,
    environment_frames,
)
from app.main import create_app
from tests.conftest import TOKEN
from tests.test_access_roles import bearer, issue

DEVICE = UUID(int=7)
START = datetime(2026, 1, 1, tzinfo=UTC)
CARD = {
    "name": "Pose baseline",
    "version": "1.0.0",
    "license": "Apache-2.0",
    "source_url": "https://example.org/models/pose",
    "sha256": "a" * 64,
    "intended_use": "Pesquisa offline; não usado em produção.",
}


def frames(count, frame_seed, environment=1, change=None):
    return environment_frames(DEVICE, START, count, environment, frame_seed, change)


def test_reference_requires_enough_frames_and_a_shared_layout():
    with pytest.raises(ValueError):
        build(frames(WINDOW, 0))
    with pytest.raises(ValueError):
        calibrate(frames(2 * WINDOW + 10, 0))  # fewer than three held-out windows


def test_same_environment_stays_normal_and_a_band_change_is_detected():
    model = calibrate(frames(400, 0))
    status, score = assess(frames(WINDOW, 1), model)
    assert status == "NORMAL" and score is not None and score <= model.threshold
    changed = frames(WINDOW, 2, change=Change(10, 20, 1.4))
    assert assess(changed, model)[0] == "CHANGED"
    assert distance(changed, model.fingerprint) > 3 * model.threshold


def test_too_few_frames_abstain_instead_of_guessing():
    model = calibrate(frames(400, 0))
    assert assess(frames(MIN_FRAMES - 1, 3), model) == ("ABSTAIN", None)


def test_evaluation_is_deterministic_bounded_and_reports_its_blind_spot():
    first, again = evaluate(42), evaluate(42)
    assert first == again
    assert first["evidence_level"] == "L0_SYNTHETIC" and first["transport"] == "SWF1"
    assert first["false_positive_rate"] <= 0.05
    assert first["detection_rate"] >= 0.9
    assert first["other_environment_detection_rate"] >= 0.9
    # Subtle changes are expected to be missed; the result must say so, not hide it.
    assert first["subtle_detection_rate"] < 0.5
    assert any("pequenas" in item for item in first["limitations"])
    assert first["abstained"] == first["sparse_windows"]
    assert evaluate(43)["fingerprint_sha256"] != first["fingerprint_sha256"]
    with pytest.raises(ValueError):
        evaluate(-1)


@pytest.fixture
def lab(settings, tmp_path):
    config = settings.model_copy(update={"rate_write": 1000, "rate_read": 1000})
    with TestClient(create_app(config)) as client:
        client.headers.update(bearer(TOKEN))
        yield client


def test_fingerprint_route_requires_operator_and_returns_the_contract(lab):
    viewer = issue(lab, "viewer")["token"]
    operator = issue(lab, "operator")["token"]
    path = "/api/v1/model-lab/rf-fingerprint/evaluations"
    assert lab.post(path, json={"seed": 1}, headers=bearer(viewer)).status_code == 403
    body = lab.post(path, json={"seed": 1}, headers=bearer(operator)).json()
    assert body["method"] == "rf-fingerprint-zscore-v1"
    assert lab.post(path, json={"seed": 100001}).status_code == 422


def test_registry_reverifies_project_artifacts_and_flags_tampering(lab):
    run = lab.post("/api/v1/model-lab/runs", json={"seed": 5})
    assert run.status_code == 200
    project = lab.get("/api/v1/model-lab/models").json()["project"]
    assert [item["integrity"] for item in project] == ["VERIFIED"]
    artifacts = lab.app.state.container.model_lab.artifacts
    path = next(artifacts.glob("model-*.json"))
    model = json.loads(path.read_text())
    model["threshold_m_per_s"] += 1  # tamper with a parameter, keep the recorded digest
    path.write_text(json.dumps(model))
    assert lab.get("/api/v1/model-lab/models").json()["project"][0]["integrity"] == "MISMATCH"
    path.write_text("{not json")
    assert lab.get("/api/v1/model-lab/models").json()["project"][0]["integrity"] == "UNREADABLE"


def test_external_cards_are_admin_only_metadata_with_license_classification(lab):
    viewer = issue(lab, "viewer")["token"]
    assert (
        lab.post("/api/v1/model-lab/models", json=CARD, headers=bearer(viewer)).status_code == 403
    )
    card = lab.post("/api/v1/model-lab/models", json=CARD).json()
    assert card["status"] == "NOT_LOADED" and card["commercial_use"] == "ALLOWED"
    assert lab.post("/api/v1/model-lab/models", json=CARD).status_code == 409  # same sha256
    restricted = CARD | {"sha256": "b" * 64, "license": "CC-BY-NC-4.0"}
    assert lab.post("/api/v1/model-lab/models", json=restricted).json()["commercial_use"] == (
        "NOT_ALLOWED"
    )
    for invalid in (
        {"source_url": "http://example.org/x"},
        {"sha256": "XYZ"},
        {"license": "WTFPL"},
        {"name": "<script>"},
        {"path": "C:/models/x.onnx"},
    ):
        assert lab.post("/api/v1/model-lab/models", json=CARD | invalid).status_code == 422
    listed = lab.get("/api/v1/model-lab/models", headers=bearer(viewer)).json()
    assert len(listed["third_party"]) == 2
    assert lab.delete(f"/api/v1/model-lab/models/{card['id']}").json() == {"removed": True}
    assert lab.delete(f"/api/v1/model-lab/models/{card['id']}").status_code == 404
    actions = [item["action"] for item in lab.get("/api/v1/governance/status").json()["audit"]]
    assert "model_registry.removed" in actions and "model_registry.registered" in actions


def test_lab_surfaces_are_refused_in_the_commercial_profile(settings):
    config = settings.model_copy(update={"capability_profile": "commercial-br"})
    with TestClient(create_app(config)) as client:
        client.headers.update(bearer(TOKEN))
        assert client.get("/api/v1/model-lab/models").status_code == 403
        evaluation = client.post("/api/v1/model-lab/rf-fingerprint/evaluations", json={})
        assert evaluation.status_code == 403
