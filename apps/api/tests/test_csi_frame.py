import random
import struct
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.domain.csi_frame import (
    HEADER,
    HEADER_SIZE,
    MAX_FRAME,
    TAG_SIZE,
    FrameError,
    FrameReceiver,
    TransportFaults,
    encode,
    parse,
    synthetic_frames,
    tag,
    transport,
)

DEVICE = UUID("00000000-0000-4000-8000-0000000000a1")
OTHER = UUID("00000000-0000-4000-8000-0000000000b2")
KEY = bytes(range(32))
KEYS = {DEVICE: KEY}
NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)


def frames(count=5, **changes):
    return [replace(frame, **changes) for frame in synthetic_frames(DEVICE, NOW, count, seed=7)]


def reason(raw, keys=KEYS):
    with pytest.raises(FrameError) as rejected:
        parse(raw, keys)
    return rejected.value.reason


def resign(raw: bytes, key=KEY) -> bytes:
    body = raw[:-TAG_SIZE]
    return body + tag(key, body)


def test_round_trip_is_exact():
    frame = frames(1)[0]
    raw = encode(frame, KEY)
    assert len(raw) == HEADER_SIZE + 4 * 64 + TAG_SIZE
    assert parse(raw, KEYS) == frame


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda raw: raw[:-1], "subcarriers"),
        (lambda raw: b"XWF1" + raw[4:], "magic"),
        (lambda raw: raw[:4] + b"\x02" + raw[5:], "version"),
        (lambda raw: raw[:-TAG_SIZE] + bytes(TAG_SIZE), "authentication"),
        (lambda raw: b"\x00" * 10, "length"),
        (lambda raw: raw + bytes(MAX_FRAME), "length"),
    ],
)
def test_structural_rejections(mutate, expected):
    raw = encode(frames(1)[0], KEY)
    assert reason(resign(mutate(raw)) if expected == "subcarriers" else mutate(raw)) == expected


def test_unpaired_device_and_wrong_key_are_refused():
    raw = encode(frames(1)[0], KEY)
    assert reason(raw, {OTHER: KEY}) == "unpaired"
    assert reason(raw, {DEVICE: bytes(32)}) == "authentication"


def test_authenticated_but_invalid_fields_are_still_refused():
    raw = encode(frames(1)[0], KEY)
    header = list(HEADER.unpack_from(raw))

    def with_field(index, value):
        header_copy = header.copy()
        header_copy[index] = value
        return resign(HEADER.pack(*header_copy) + raw[HEADER_SIZE:])

    assert reason(with_field(2, 0x80)) == "reserved_bits"  # unknown flag
    assert reason(with_field(12, 1)) == "reserved_bits"
    assert reason(with_field(7, 0)) == "radio"  # channel 0
    assert reason(with_field(8, 9)) == "radio"  # bandwidth code
    assert reason(with_field(9, 5)) == "radio"  # positive RSSI
    assert reason(with_field(11, 65)) == "subcarriers"  # count disagrees with length
    assert reason(with_field(6, 2**64 - 1)) == "timestamp"


def test_receiver_enforces_freshness_replay_order_and_hardware_gate():
    receiver = FrameReceiver(KEYS, clock=lambda: NOW + timedelta(seconds=1))
    first, second, third = (encode(frame, KEY) for frame in frames(3))
    assert receiver.receive(second) is not None
    assert receiver.receive(first) is None  # older sequence after a newer one
    assert receiver.receive(second) is None  # replay
    assert receiver.receive(third) is not None
    stale = encode(frames(1, timestamp=NOW - timedelta(minutes=5), sequence=10)[0], KEY)
    future = encode(frames(1, timestamp=NOW + timedelta(seconds=30), sequence=11)[0], KEY)
    real = encode(frames(1, synthetic=False, sequence=12)[0], KEY)
    assert receiver.receive(stale) is None
    assert receiver.receive(future) is None
    assert receiver.receive(real) is None
    assert receiver.accepted == 2
    assert receiver.rejected == {
        "replay_or_out_of_order": 2,
        "stale": 2,
        "hardware_not_tested": 1,
    }


def test_receiver_requires_strong_keys_and_bounded_pairing():
    with pytest.raises(ValueError):
        FrameReceiver({DEVICE: b"short"})
    with pytest.raises(ValueError):
        FrameReceiver({UUID(int=index): KEY for index in range(33)})


def test_fuzzed_frames_only_raise_frame_error_and_are_never_accepted():
    """Deterministic mutation fuzzing: flips, truncation, extension, splices and noise."""
    randomizer = random.Random(20261017)
    originals = [encode(frame, KEY) for frame in synthetic_frames(DEVICE, NOW, 20, seed=1)]
    reasons = set()
    for _ in range(20000):
        raw = bytearray(randomizer.choice(originals))
        operation = randomizer.randrange(5)
        if operation == 0:
            for _ in range(randomizer.randint(1, 8)):
                raw[randomizer.randrange(len(raw))] ^= 1 << randomizer.randrange(8)
        elif operation == 1:
            raw = raw[: randomizer.randrange(len(raw))]
        elif operation == 2:
            raw += randomizer.randbytes(randomizer.randint(1, 64))
        elif operation == 3:
            other = randomizer.choice(originals)
            cut = randomizer.randrange(len(raw))
            raw = raw[:cut] + other[cut:]
        else:
            raw = bytearray(randomizer.randbytes(randomizer.randint(0, MAX_FRAME + 8)))
        candidate = bytes(raw)
        if candidate in originals:
            continue  # a splice can reproduce a genuine frame
        try:
            parse(candidate, KEYS)
        except FrameError as error:
            reasons.add(error.reason)
        else:
            raise AssertionError("a mutated frame passed authentication")
    assert {"length", "magic", "authentication"} <= reasons


def test_fuzzed_authenticated_headers_never_crash():
    """With a valid tag recomputed, random header values exercise semantic checks."""
    randomizer = random.Random(99)
    base = encode(frames(1)[0], KEY)
    for _ in range(5000):
        header = bytearray(base[:HEADER_SIZE])
        header[4:HEADER_SIZE] = randomizer.randbytes(HEADER_SIZE - 4)
        header[8:24] = DEVICE.bytes  # keep the paired device so the tag is checked
        header[5] = randomizer.choice([0, 1, 2, 255])
        raw = resign(bytes(header) + base[HEADER_SIZE:])
        try:
            frame = parse(raw, KEYS)
        except FrameError:
            continue
        assert 1 <= frame.channel <= 233 and frame.rssi_dbm <= 0
        assert len(frame.iq) == 64


def test_transport_faults_are_counted_and_never_corrupt_accepted_data():
    clean = synthetic_frames(DEVICE, NOW, 400, seed=3)
    wire = [encode(frame, KEY) for frame in clean]
    faults = TransportFaults(loss=0.1, duplicate=0.1, reorder=0.1, corrupt=0.05)
    received, injected = transport(wire, faults, seed=11)
    receiver = FrameReceiver(KEYS, clock=lambda: NOW + timedelta(seconds=40))
    accepted = [frame for raw in received if (frame := receiver.receive(raw))]
    assert receiver.accepted + sum(receiver.rejected.values()) == len(received)
    assert len(received) == 400 - injected["loss"] + injected["duplicate"]
    assert receiver.accepted <= 400 - injected["loss"]
    assert all(frame == clean[frame.sequence] for frame in accepted)
    sequences = [frame.sequence for frame in accepted]
    assert sequences == sorted(set(sequences))
    assert receiver.rejected["replay_or_out_of_order"] >= injected["duplicate"]
    assert set(receiver.rejected) <= {
        "replay_or_out_of_order",
        "authentication",
        "magic",
        "version",
        "unpaired",
    }


def test_duplicates_alone_are_exactly_the_replays():
    wire = [encode(frame, KEY) for frame in synthetic_frames(DEVICE, NOW, 200, seed=5)]
    received, injected = transport(wire, TransportFaults(duplicate=0.25), seed=2)
    receiver = FrameReceiver(KEYS, clock=lambda: NOW + timedelta(seconds=30))
    for raw in received:
        receiver.receive(raw)
    assert receiver.accepted == 200
    assert receiver.rejected == {"replay_or_out_of_order": injected["duplicate"]}


def test_header_layout_is_the_documented_44_bytes():
    assert HEADER_SIZE == 44
    assert struct.calcsize("<hh") == 4
