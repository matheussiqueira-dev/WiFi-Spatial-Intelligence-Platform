"""Project-owned offline packet prototype. No network, CSI or physical receiver."""

import hashlib
import json
import math
from datetime import UTC, datetime


def encode(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def synthetic_packet(sensor_id, sequence, timestamp):
    data = {
        "schema_version": "1.0",
        "sensor_id": sensor_id,
        "sequence": sequence,
        "timestamp": timestamp.isoformat(),
        "samples": [0.1, 0.2, 0.3],
        "evidence_level": "L0_SYNTHETIC",
        "modality": "SYNTHETIC_TEST_SIGNAL",
    }
    return encode({**data, "checksum": hashlib.sha256(encode(data)).hexdigest()})


class PacketReceiver:
    def __init__(self, paired: set[str], clock=lambda: datetime.now(UTC)):
        if len(paired) > 32 or any(not p.startswith("virtual-packet-") for p in paired):
            raise ValueError("only bounded virtual pairing supported")
        self.paired = frozenset(paired)
        self.clock = clock
        self.last = {}

    def receive(self, raw: bytes, *, authorized=False):
        if not authorized:
            raise ValueError("explicit offline authorization required")
        if len(raw) > 8192:
            raise ValueError("packet size limit")
        try:
            data = json.loads(raw)
            if not isinstance(data, dict) or set(data) != {
                "schema_version",
                "sensor_id",
                "sequence",
                "timestamp",
                "samples",
                "evidence_level",
                "modality",
                "checksum",
            }:
                raise ValueError("unsupported packet fields")
            checksum = data.pop("checksum")
            if checksum != hashlib.sha256(encode(data)).hexdigest():
                raise ValueError("packet checksum mismatch")
            if data["schema_version"] != "1.0" or data["evidence_level"] != "L0_SYNTHETIC":
                raise ValueError("only synthetic schema supported")
            if data["modality"] != "SYNTHETIC_TEST_SIGNAL":
                raise ValueError("real acquisition unavailable")
            sensor = data["sensor_id"]
            if sensor not in self.paired:
                raise ValueError("sensor not paired")
            sequence = data["sequence"]
            if type(sequence) is not int or not 0 <= sequence < 2**32:
                raise ValueError("invalid sequence")
            timestamp = datetime.fromisoformat(data["timestamp"])
            if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
                raise ValueError("UTC required")
            age = (self.clock() - timestamp).total_seconds()
            if not -2 <= age <= 60:
                raise ValueError("clock skew or stale packet")
            prior = self.last.get(sensor)
            if prior and (sequence <= prior[0] or timestamp < prior[1]):
                raise ValueError("packet out of order")
            samples = data["samples"]
            if not isinstance(samples, list) or not 1 <= len(samples) <= 128:
                raise ValueError("sample count limit")
            if any(
                type(v) not in {int, float} or not math.isfinite(v) or abs(v) > 1e6 for v in samples
            ):
                raise ValueError("invalid sample")
            self.last[sensor] = (sequence, timestamp)
            return data
        except (TypeError, KeyError, UnicodeError, OverflowError, RecursionError) as error:
            raise ValueError("malformed synthetic packet") from error
