import asyncio
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.contracts import SensingEvent, SimulationConfig
from app.simulator import SimulationProvider


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
@pytest.mark.parametrize("occupants", [0, 2, 20])
def test_scenarios_are_bounded_synthetic_and_reproducible(scenario, occupants):
    config = SimulationConfig(scenario=scenario, occupants=occupants, seed=41)
    left, right = SimulationProvider(config), SimulationProvider(config)
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    observed = []
    for _ in range(60):
        a, b = left.sample(timestamp), right.sample(timestamp)
        assert (a is None) == (b is None)
        if a:
            assert a.measurements == b.measurements
            assert a.provenance == b.provenance
            assert a.evidence_level == "L0_SYNTHETIC"
            assert a.quality.confidence is None and a.model.id is None
            assert SensingEvent.model_validate_json(a.model_dump_json()) == a
            observed.append(a)
    if scenario == "empty":
        assert all(e.measurements.occupancy_estimate == 0 for e in observed)
    if scenario == "stationary":
        assert observed[0].measurements == observed[-1].measurements
    if scenario == "entering":
        assert observed[0].measurements.occupancy_estimate == 0
        assert observed[-1].measurements.occupancy_estimate == min(occupants, 19)
    if scenario == "leaving":
        assert observed[0].measurements.occupancy_estimate == occupants
        assert observed[-1].measurements.occupancy_estimate == max(0, occupants - 19)
    if scenario == "disconnect":
        assert len(observed) == 5
    if scenario == "packet_loss":
        assert 0 < len(observed) < 60


@pytest.mark.parametrize(
    "config",
    [
        {"occupants": -1},
        {"occupants": 21},
        {"seed": -1},
        {"speed": 0},
        {"speed": float("nan")},
        {"scenario": "real_csi"},
        {"unexpected": True},
    ],
)
def test_invalid_config_rejected(config):
    with pytest.raises(ValidationError):
        SimulationConfig(**config)


def test_inference_and_inconsistent_presence_rejected():
    sample = SimulationProvider(SimulationConfig()).sample().model_dump(mode="json")
    sample["model"]["id"] = "unvalidated-model"
    with pytest.raises(ValidationError):
        SensingEvent.model_validate(sample)
    sample["model"]["id"] = None
    sample["measurements"]["presence_detected"] = False
    with pytest.raises(ValidationError):
        SensingEvent.model_validate(sample)
    sample["measurements"]["presence_detected"] = True
    sample["quality"]["confidence"] = 0.99
    with pytest.raises(ValidationError):
        SensingEvent.model_validate(sample)


def test_provider_stream_survives_a_lost_packet():
    async def check():
        provider = SimulationProvider(SimulationConfig(scenario="packet_loss", seed=43, speed=4))
        await provider.connect()
        stream = provider.read_events()
        sample = await asyncio.wait_for(anext(stream), 2)
        assert sample.provenance.tick > 0
        assert provider.connected
        await stream.aclose()
        await provider.disconnect()

    asyncio.run(check())
