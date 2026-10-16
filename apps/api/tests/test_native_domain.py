import ast
from pathlib import Path

import pytest


def test_native_scene_is_repeatable_bounded_and_synthetic():
    from app.domain.acquisition import SyntheticScene

    for scenario in (
        "empty",
        "stationary",
        "walking",
        "entering",
        "leaving",
        "interference",
        "packet_loss",
        "disconnect",
    ):
        left = SyntheticScene(seed=42, occupants=20, scenario=scenario)
        right = SyntheticScene(seed=42, occupants=20, scenario=scenario)
        for tick in range(30):
            sample = left.sample(tick)
            assert sample == right.sample(tick)
            if sample is not None:
                assert sample.evidence_level == "L0_SYNTHETIC"
                assert sample.occupancy == len(sample.positions)
                assert sample.presence == (sample.occupancy > 0)
                assert all(0 <= x <= 8 and 0 <= y <= 6 for x, y in sample.positions)


def test_native_scene_rejects_invalid_inputs():
    from app.domain.acquisition import SyntheticScene

    for arguments in ({"occupants": 21}, {"seed": -1}, {"scenario": "real"}):
        with pytest.raises(ValueError):
            SyntheticScene(**arguments)


def test_domain_has_no_framework_storage_or_legacy_imports():
    directory = Path(__file__).parents[1] / "app/domain"
    files = list(directory.rglob("*.py"))
    assert files
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            assert not any(
                any(
                    fragment in name
                    for fragment in (
                        "fastapi",
                        "sqlalchemy",
                        "pydantic",
                        "ruview",
                        "app.adapters",
                        "app.storage",
                    )
                )
                for name in names
            ), path


def test_legacy_is_off_by_default(client):
    result = client.post("/api/v1/sources/select", json={"source": "RUVIEW_STREAM"})
    assert result.status_code == 409
    assert client.get("/api/v1/system/status").json()["provider"] == "synthetic-native"


def test_default_startup_does_not_import_legacy_engine():
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from app.main import create_app; from app.config import Settings; import sys; "
                "app=create_app(Settings(token='test-only-'+'x'*40, _env_file=None)); "
                "assert 'app.ruview' not in sys.modules; "
                "assert app.state.pipeline.source == 'synthetic-native'"
            ),
        ],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
