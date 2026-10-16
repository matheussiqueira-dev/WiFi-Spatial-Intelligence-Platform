"""Bounded analysis of host link measurements, never RF inference."""

from datetime import datetime
from statistics import mean
from typing import Sequence

from app.network_contracts import NetworkSample, NetworkSummary


def summarize(samples: Sequence[NetworkSample], now: datetime) -> NetworkSummary:
    rows = sorted(samples, key=lambda row: (row.timestamp, str(row.sample_id)))
    connected = sum(row.link_state == "CONNECTED" for row in rows)
    disconnected = sum(row.link_state == "DISCONNECTED" for row in rows)
    signals = [row.signal_percent for row in rows if row.signal_percent is not None]
    latency = sorted(value for row in rows for value in row.probe_rtt_ms)
    sent = sum(row.probe_sent for row in rows)
    transitions = 0
    missing = 0.0
    previous: dict[str, NetworkSample] = {}
    for row in rows:
        key = str(row.collector_id)
        prior = previous.get(key)
        if prior:
            delta = (row.timestamp - prior.timestamp).total_seconds()
            if delta > 45:
                missing += delta
            elif prior.location == row.location:
                transitions += prior.link_state == "CONNECTED" and row.link_state == "DISCONNECTED"
        previous[key] = row
    last = rows[-1].timestamp if rows else None
    return NetworkSummary(
        samples=len(rows),
        connected_samples=connected,
        disconnected_samples=disconnected,
        unavailable_samples=len(rows) - connected - disconnected,
        connected_percent=100 * connected / (connected + disconnected)
        if connected + disconnected
        else None,
        signal_mean_percent=mean(signals) if signals else None,
        signal_min_percent=min(signals) if signals else None,
        gateway_mean_ms=mean(latency) if latency else None,
        gateway_p95_ms=latency[int((len(latency) - 1) * 0.95)] if latency else None,
        gateway_loss_percent=100 * (sent - len(latency)) / sent if sent else None,
        disconnect_events=transitions,
        missing_seconds=missing,
        last_seen=last,
        collector_stale=last is None or (now - last).total_seconds() > 45,
    )
