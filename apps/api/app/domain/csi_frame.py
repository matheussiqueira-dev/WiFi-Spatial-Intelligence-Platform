"""SWF1: project-owned binary frame for CSI sensors (ESP32-S3 target).

Specification: docs/CSI_FRAME_PROTOCOL.md.

Written from the public ESP-IDF CSI concepts (channel, bandwidth, RSSI, I/Q per
subcarrier) only; no upstream firmware or parser code was used. Every frame is
authenticated per paired device before any field is trusted, and the receiver rejects
replays and out-of-order sequences. Hardware frames remain NOT_TESTED until a real
board is connected; the simulator below produces frames flagged as synthetic.
"""

import hashlib
import hmac
import random
import struct
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

MAGIC = b"SWF1"
VERSION = 1
# magic, version, flags, header length, device id, sequence, timestamp (µs since epoch, UTC),
# channel, bandwidth code, RSSI (dBm), noise floor (dBm), subcarriers, reserved.
HEADER = struct.Struct("<4sBBH16sIQBBbbHH")
HEADER_SIZE = HEADER.size  # 44
TAG_SIZE = 16
MAX_SUBCARRIERS = 512
MIN_FRAME = HEADER_SIZE + 4 + TAG_SIZE
MAX_FRAME = HEADER_SIZE + 4 * MAX_SUBCARRIERS + TAG_SIZE
FLAG_SYNTHETIC = 0x01
KNOWN_FLAGS = FLAG_SYNTHETIC
BANDWIDTHS = {0: 20, 1: 40, 2: 80, 3: 160}
MAX_FUTURE = timedelta(seconds=2)
MAX_AGE = timedelta(seconds=60)


class FrameError(ValueError):
    """Rejected frame; ``reason`` is a fixed code safe to count and expose."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class CsiFrame:
    device_id: UUID
    sequence: int
    timestamp: datetime
    channel: int
    bandwidth_mhz: int
    rssi_dbm: int
    noise_floor_dbm: int
    synthetic: bool
    iq: tuple[tuple[int, int], ...]


def tag(key: bytes, body: bytes) -> bytes:
    return hmac.new(key, body, hashlib.sha256).digest()[:TAG_SIZE]


def encode(frame: CsiFrame, key: bytes) -> bytes:
    microseconds = int(frame.timestamp.timestamp() * 1_000_000)
    code = {mhz: value for value, mhz in BANDWIDTHS.items()}[frame.bandwidth_mhz]
    header = HEADER.pack(
        MAGIC,
        VERSION,
        FLAG_SYNTHETIC if frame.synthetic else 0,
        HEADER_SIZE,
        frame.device_id.bytes,
        frame.sequence,
        microseconds,
        frame.channel,
        code,
        frame.rssi_dbm,
        frame.noise_floor_dbm,
        len(frame.iq),
        0,
    )
    payload = b"".join(struct.pack("<hh", i, q) for i, q in frame.iq)
    return header + payload + tag(key, header + payload)


def parse(raw: bytes, keys: Mapping[UUID, bytes]) -> CsiFrame:
    """Stateless validation of one frame. Raises FrameError, never anything else."""
    if not isinstance(raw, (bytes, bytearray)):
        raise FrameError("not_bytes")
    if not MIN_FRAME <= len(raw) <= MAX_FRAME:
        raise FrameError("length")
    (
        magic,
        version,
        flags,
        header_size,
        device,
        sequence,
        microseconds,
        channel,
        bandwidth,
        rssi,
        noise,
        subcarriers,
        reserved,
    ) = HEADER.unpack_from(raw)
    if magic != MAGIC:
        raise FrameError("magic")
    if version != VERSION or header_size != HEADER_SIZE:
        raise FrameError("version")
    device_id = UUID(bytes=bytes(device))
    key = keys.get(device_id)
    if key is None:
        raise FrameError("unpaired")
    # Authenticate before trusting any length or semantic field.
    body, received = bytes(raw[:-TAG_SIZE]), bytes(raw[-TAG_SIZE:])
    if not hmac.compare_digest(tag(key, body), received):
        raise FrameError("authentication")
    if flags & ~KNOWN_FLAGS or reserved != 0:
        raise FrameError("reserved_bits")
    if not 1 <= subcarriers <= MAX_SUBCARRIERS or len(raw) != MIN_FRAME - 4 + 4 * subcarriers:
        raise FrameError("subcarriers")
    if not 1 <= channel <= 233 or bandwidth not in BANDWIDTHS:
        raise FrameError("radio")
    if not -127 <= rssi <= 0 or not -127 <= noise <= 0:
        raise FrameError("radio")
    try:
        timestamp = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(microseconds=microseconds)
    except OverflowError as error:
        raise FrameError("timestamp") from error
    iq = tuple(struct.iter_unpack("<hh", body[HEADER_SIZE:]))
    return CsiFrame(
        device_id=device_id,
        sequence=sequence,
        timestamp=timestamp,
        channel=channel,
        bandwidth_mhz=BANDWIDTHS[bandwidth],
        rssi_dbm=rssi,
        noise_floor_dbm=noise,
        synthetic=bool(flags & FLAG_SYNTHETIC),
        iq=iq,
    )


class FrameReceiver:
    """Stateful receiver: freshness, replay and ordering per device, with reason counts."""

    def __init__(
        self,
        keys: Mapping[UUID, bytes],
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        *,
        accept_hardware: bool = False,
    ):
        if len(keys) > 32 or any(len(key) < 32 for key in keys.values()):
            raise ValueError("at most 32 paired devices with 32-byte keys")
        self.keys = dict(keys)
        self.clock = clock
        # Real frames stay refused until a board is validated (status NOT_TESTED).
        self.accept_hardware = accept_hardware
        self.last_sequence: dict[UUID, int] = {}
        self.accepted = 0
        self.rejected: Counter[str] = Counter()

    def receive(self, raw: bytes) -> CsiFrame | None:
        try:
            frame = parse(raw, self.keys)
            if not frame.synthetic and not self.accept_hardware:
                raise FrameError("hardware_not_tested")
            age = self.clock() - frame.timestamp
            if age < -MAX_FUTURE or age > MAX_AGE:
                raise FrameError("stale")
            if frame.sequence <= self.last_sequence.get(frame.device_id, -1):
                raise FrameError("replay_or_out_of_order")
        except FrameError as error:
            self.rejected[error.reason] += 1
            return None
        self.last_sequence[frame.device_id] = frame.sequence
        self.accepted += 1
        return frame


def synthetic_frames(
    device_id: UUID, start: datetime, count: int, seed: int, subcarriers: int = 64
) -> list[CsiFrame]:
    """Deterministic test signal; values carry no physical meaning."""
    randomizer = random.Random(f"swf1:{device_id}:{seed}")
    return [
        CsiFrame(
            device_id=device_id,
            sequence=index,
            timestamp=start + timedelta(milliseconds=100 * index),
            channel=149,
            bandwidth_mhz=80,
            rssi_dbm=randomizer.randint(-80, -30),
            noise_floor_dbm=-95,
            synthetic=True,
            iq=tuple(
                (randomizer.randint(-2048, 2047), randomizer.randint(-2048, 2047))
                for _ in range(subcarriers)
            ),
        )
        for index in range(count)
    ]


@dataclass(frozen=True)
class TransportFaults:
    loss: float = 0.0
    duplicate: float = 0.0
    reorder: float = 0.0
    corrupt: float = 0.0


def transport(
    frames: Iterable[bytes], faults: TransportFaults, seed: int
) -> tuple[list[bytes], Counter[str]]:
    """Apply loss, duplication, adjacent reordering and bit corruption, counting each."""
    randomizer = random.Random(seed)
    injected: Counter[str] = Counter()
    output: list[bytes] = []
    for frame in frames:
        if randomizer.random() < faults.loss:
            injected["loss"] += 1
            continue
        if randomizer.random() < faults.corrupt:
            position = randomizer.randrange(len(frame))
            frame = (
                frame[:position]
                + bytes([frame[position] ^ (1 << randomizer.randrange(8))])
                + frame[position + 1 :]
            )
            injected["corrupt"] += 1
        output.append(frame)
        if randomizer.random() < faults.duplicate:
            output.append(frame)
            injected["duplicate"] += 1
        if len(output) >= 2 and randomizer.random() < faults.reorder:
            output[-1], output[-2] = output[-2], output[-1]
            injected["reorder"] += 1
    return output, injected
