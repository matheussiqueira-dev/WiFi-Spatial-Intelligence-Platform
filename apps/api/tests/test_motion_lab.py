import copy
import json
import os

import pytest

from app.application import model_lab
from app.application.model_lab import ExperimentRequest, ModelLab
from app.domain.motion import checksum, evaluate_baseline, extract_window, prepare_dataset


def test_features_reject_gaps_and_unknown_and_do_not_read_labels():
    assert extract_window([(0, 0, 0), (1, 1, 0), (2, 2, 0)]) == 1
    assert extract_window([(0, 0, 0), (10, 1, 0), (11, 2, 0)]) is None
    assert extract_window([(0, 0, 0)]) is None
    assert extract_window([(0, 0, 0), (0, 1, 0), (1, 2, 0)]) is None


def test_window_abstains_when_any_point_leaves_the_room():
    assert extract_window([(0, -50, -50), (1, 1, 0), (2, 2, 0)]) is None
    assert extract_window([(0, 0, 7), (1, 1, 0), (2, 2, 0)]) is None
    assert extract_window([(0, 0, 0), (1, 1, 0), (2, 9, 0)]) is None


def test_dataset_splits_determinism_and_evaluation():
    data = prepare_dataset(42)
    assert data == prepare_dataset(42)
    sessions = [
        {row["session_id"] for row in data[split]} for split in ("train", "validation", "test")
    ]
    assert not sessions[0] & sessions[1] and not sessions[0] & sessions[2]
    assert not sessions[1] & sessions[2]
    configs = [{r["sample_spacing"] for r in data[s]} for s in data]
    assert not configs[0] & configs[1] and not configs[1] & configs[2]
    result = evaluate_baseline(data)
    assert result == evaluate_baseline(data)
    assert result["evidence_level"] == "L0_SYNTHETIC"
    assert (
        sum(sum(row) for row in result["evaluation"]["confusion_matrix"])
        == result["evaluation"]["samples"]
    )
    changed = copy.deepcopy(data)
    for row in changed["test"]:
        row["reference"] = "stationary"
    assert evaluate_baseline(changed)["model"] == result["model"]
    assert set(result["unsupported"]) >= {"sitting", "possible_fall", "rf_fingerprint"}


def test_leakage_rejected_and_empty_metrics_are_null():
    dataset = prepare_dataset(1)
    dataset["test"][0]["session_id"] = dataset["train"][0]["session_id"]
    with pytest.raises(ValueError, match="leakage"):
        evaluate_baseline(dataset)
    dataset = prepare_dataset(1)
    dataset["test"] = []
    result = evaluate_baseline(dataset)["evaluation"]
    assert result["samples"] == 0 and result["accuracy_accepted"] is None
    assert result["false_positive_rate"] is None and result["rejection_rate"] is None


def test_lab_api_roundtrip_and_reopen(settings):
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app(settings)) as client:
        assert client.post("/api/v1/model-lab/runs", json={"seed": 42}).status_code == 401
        client.headers["Authorization"] = f"Bearer {settings.token}"
        assert client.post("/api/v1/model-lab/runs", json={"seed": -1}).status_code == 422
        assert client.post("/api/v1/model-lab/runs", json={"path": "../secret"}).status_code == 422
        response = client.post("/api/v1/model-lab/runs", json={"seed": 42})
        assert response.status_code == 200
        run = response.json()
        assert run["evidence_level"] == "L0_SYNTHETIC"
        assert len(run["model"]["sha256"]) == 64
        identifier = run["id"]
        assert client.get("/api/v1/model-lab/runs?limit=1").json()["total"] == 1
        assert client.get("/api/v1/model-lab/runs?limit=201").status_code == 422
    with TestClient(create_app(settings)) as client:
        client.headers["Authorization"] = f"Bearer {settings.token}"
        assert client.get(f"/api/v1/model-lab/runs/{identifier}").json() == run
        assert "ground_truth_positions" not in json.dumps(run)


def test_partial_artifacts_are_repaired_without_blocking_the_seed(client, tmp_path):
    lab = ModelLab(client.app.state.store, tmp_path / "lab")
    dataset = prepare_dataset(7)
    payload = json.dumps(dataset, sort_keys=True, allow_nan=False)
    (tmp_path / "lab").mkdir()
    target = tmp_path / "lab" / f"dataset-{checksum(dataset)}.json"
    # A torn write from an interrupted process must not lock this seed out forever.
    target.write_text(payload[:4096], encoding="utf-8")
    result = lab.execute(ExperimentRequest(seed=7))
    assert target.read_text(encoding="utf-8") == payload
    model_target = tmp_path / "lab" / f"model-{result['model']['sha256']}.json"
    model_payload = json.dumps(result["model"], sort_keys=True, allow_nan=False)
    assert model_target.read_text(encoding="utf-8") == model_payload
    model_target.write_text(model_payload[:10], encoding="utf-8")
    lab.execute(ExperimentRequest(seed=7))
    assert model_target.read_text(encoding="utf-8") == model_payload
    assert {p.name for p in (tmp_path / "lab").iterdir()} == {target.name, model_target.name}


def test_failed_artifact_write_leaves_no_partial_file(client, tmp_path, monkeypatch):
    store = client.app.state.store
    lab = ModelLab(store, tmp_path / "lab")

    def interrupted(*_):
        raise OSError("simulated interruption before rename")

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", interrupted)
        with pytest.raises(OSError):
            lab.execute(ExperimentRequest(seed=8))
    assert list((tmp_path / "lab").iterdir()) == []
    assert store.model_runs()["total"] == 0
    assert lab.execute(ExperimentRequest(seed=8))["seed"] == 8


def test_result_is_validated_before_it_is_persisted(client, tmp_path, monkeypatch):
    store = client.app.state.store
    original = model_lab.evaluate_baseline

    def drifted(dataset):
        return {**original(dataset), "unexpected_metric": 1.0}

    monkeypatch.setattr(model_lab, "evaluate_baseline", drifted)
    with pytest.raises(RuntimeError, match="contract"):
        ModelLab(store, tmp_path / "lab").execute(ExperimentRequest(seed=9))
    assert store.model_runs()["total"] == 0
