"""Restricted preview predicates. No expressions, scripts, URLs or dispatch."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleSpec:
    name: str
    field: str
    threshold: int

    def __post_init__(self):
        if not 1 <= len(self.name) <= 60 or self.field not in {"presence", "occupancy"}:
            raise ValueError("unsupported rule")
        if type(self.threshold) is not int or not 0 <= self.threshold <= 20:
            raise ValueError("threshold must be integer 0..20")
        if self.field == "presence" and self.threshold not in {0, 1}:
            raise ValueError("presence threshold must be 0 or 1")


def matches(rule: RuleSpec, measurements: dict) -> bool:
    if rule.field == "presence":
        return measurements.get("presence_detected") is bool(rule.threshold)
    count = measurements.get("occupancy_estimate")
    return type(count) is int and count >= rule.threshold
