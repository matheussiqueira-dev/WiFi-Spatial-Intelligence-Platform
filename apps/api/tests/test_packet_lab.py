import json
import random
from datetime import UTC, datetime

import pytest

from app.domain.packet_lab import PacketReceiver, synthetic_packet

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_pairing_integrity_time_and_replay():
    receiver = PacketReceiver({"virtual-packet-1"}, lambda: NOW)
    packet = synthetic_packet("virtual-packet-1", 1, NOW)
    with pytest.raises(ValueError, match="authorization"):
        receiver.receive(packet)
    accepted = receiver.receive(packet, authorized=True)
    assert accepted["evidence_level"] == "L0_SYNTHETIC"
    assert accepted["modality"] == "SYNTHETIC_TEST_SIGNAL"
    with pytest.raises(ValueError, match="order"):
        receiver.receive(packet, authorized=True)
    changed = json.loads(synthetic_packet("virtual-packet-1", 2, NOW))
    changed["samples"][0] = 123
    with pytest.raises(ValueError, match="checksum"):
        receiver.receive(json.dumps(changed).encode(), authorized=True)
    with pytest.raises(ValueError, match="paired"):
        receiver.receive(synthetic_packet("virtual-packet-2", 2, NOW), authorized=True)


def test_malformed_packets_bounded_fuzz():
    receiver = PacketReceiver({"virtual-packet-1"}, lambda: NOW)
    randomizer = random.Random(42)
    for _ in range(200):
        payload = randomizer.randbytes(randomizer.randrange(0, 9000))
        with pytest.raises(ValueError):
            receiver.receive(payload, authorized=True)
    for value in [b"{}", b"[]", b"null", b"x" * 8193]:
        with pytest.raises(ValueError):
            receiver.receive(value, authorized=True)
