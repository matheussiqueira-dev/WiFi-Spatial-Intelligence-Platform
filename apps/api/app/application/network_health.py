"""Hourly link trend and advisory degradation alerts over measured host telemetry.

Alerts compare the most recent window with the preceding baseline of the same location
filter. They are advice for the operator: nothing is dispatched, and an alert never
claims a cause (interference, router fault, people) that the data cannot show.
"""

from datetime import datetime, timedelta
from typing import Sequence

from app.application.network_diagnostics import summarize
from app.network_contracts import (
    DegradationAlert,
    NetworkHealth,
    NetworkSample,
    NetworkSummary,
    NetworkTrendBucket,
)

RECENT = timedelta(hours=1)
# Thresholds are deliberately conservative and published in the response.
SIGNAL_DROP_POINTS = 15
LATENCY_FACTOR = 2.0
LATENCY_MARGIN_MS = 20.0
LOSS_PERCENT = 5.0
DISCONNECTS = 3
MIN_SIGNAL_SAMPLES = 5
MIN_REPLIES = 10
MIN_PROBES = 10


def _signal_samples(rows: Sequence[NetworkSample]) -> int:
    return sum(row.signal_percent is not None for row in rows)


def _replies(rows: Sequence[NetworkSample]) -> int:
    return sum(len(row.probe_rtt_ms) for row in rows)


def trend(
    rows: Sequence[NetworkSample], start: datetime, end: datetime, bucket: timedelta
) -> list[NetworkTrendBucket]:
    buckets = []
    cursor = start
    while cursor < end:
        upper = min(cursor + bucket, end)
        inside = [row for row in rows if cursor <= row.timestamp < upper]
        # A bucket's staleness is judged at its own end, not at "now".
        buckets.append(
            NetworkTrendBucket(start=cursor, end=upper, summary=summarize(inside, upper))
        )
        cursor = upper
    return buckets


def degradation(
    rows: Sequence[NetworkSample], now: datetime
) -> tuple[list[DegradationAlert], list[str], NetworkSummary, NetworkSummary]:
    recent_rows = [row for row in rows if row.timestamp >= now - RECENT]
    baseline_rows = [row for row in rows if row.timestamp < now - RECENT]
    recent = summarize(recent_rows, now)
    baseline = summarize(baseline_rows, now - RECENT)
    alerts: list[DegradationAlert] = []
    abstentions: list[str] = []

    if recent.collector_stale:
        alerts.append(
            DegradationAlert(
                code="COLLECTOR_STALE",
                severity="info",
                metric="last_seen",
                recent=None,
                baseline=None,
                threshold=45,
                message="Coletor sem amostra há mais de 45 s; não comprova queda da rede.",
            )
        )

    if (
        _signal_samples(recent_rows) >= MIN_SIGNAL_SAMPLES
        and _signal_samples(baseline_rows) >= MIN_SIGNAL_SAMPLES
        and recent.signal_mean_percent is not None
        and baseline.signal_mean_percent is not None
    ):
        drop = baseline.signal_mean_percent - recent.signal_mean_percent
        if drop >= SIGNAL_DROP_POINTS:
            alerts.append(
                DegradationAlert(
                    code="SIGNAL_DROP",
                    severity="warning",
                    metric="signal_mean_percent",
                    recent=recent.signal_mean_percent,
                    baseline=baseline.signal_mean_percent,
                    threshold=SIGNAL_DROP_POINTS,
                    message=(
                        f"Sinal médio caiu {drop:.0f} pontos na última hora em relação "
                        "à linha de base; verifique se o computador mudou de lugar."
                    ),
                )
            )
    else:
        abstentions.append("signal: menos de 5 leituras de sinal na hora recente ou na base")

    if (
        _replies(recent_rows) >= MIN_REPLIES
        and _replies(baseline_rows) >= MIN_REPLIES
        and recent.gateway_p95_ms is not None
        and baseline.gateway_p95_ms is not None
    ):
        limit = max(
            LATENCY_FACTOR * baseline.gateway_p95_ms, baseline.gateway_p95_ms + LATENCY_MARGIN_MS
        )
        if recent.gateway_p95_ms >= limit:
            alerts.append(
                DegradationAlert(
                    code="LATENCY_RISE",
                    severity="warning",
                    metric="gateway_p95_ms",
                    recent=recent.gateway_p95_ms,
                    baseline=baseline.gateway_p95_ms,
                    threshold=limit,
                    message="Latência p95 até o roteador ao menos dobrou na última hora.",
                )
            )
    else:
        abstentions.append("latency: menos de 10 respostas de sonda na hora recente ou na base")

    sent = sum(row.probe_sent for row in recent_rows)
    if sent >= MIN_PROBES and recent.gateway_loss_percent is not None:
        if recent.gateway_loss_percent >= LOSS_PERCENT:
            alerts.append(
                DegradationAlert(
                    code="PACKET_LOSS",
                    severity="warning",
                    metric="gateway_loss_percent",
                    recent=recent.gateway_loss_percent,
                    baseline=baseline.gateway_loss_percent,
                    threshold=LOSS_PERCENT,
                    message="Sondas ao roteador sem resposta acima de 5% na última hora; "
                    "ICMP pode estar limitado pelo roteador.",
                )
            )
    else:
        abstentions.append("loss: menos de 10 sondas enviadas na hora recente")

    if recent.disconnect_events >= DISCONNECTS:
        alerts.append(
            DegradationAlert(
                code="FREQUENT_DISCONNECTS",
                severity="warning",
                metric="disconnect_events",
                recent=recent.disconnect_events,
                baseline=baseline.disconnect_events,
                threshold=DISCONNECTS,
                message="Três ou mais desconexões na última hora.",
            )
        )
    return alerts, abstentions, recent, baseline


def health(
    rows: Sequence[NetworkSample],
    start: datetime,
    now: datetime,
    bucket: timedelta,
    location: str | None,
) -> NetworkHealth:
    alerts, abstentions, recent, baseline = degradation(rows, now)
    return NetworkHealth(
        start=start,
        end=now,
        location=location,
        bucket_minutes=int(bucket.total_seconds() // 60),
        buckets=trend(rows, start, now, bucket),
        recent=recent,
        baseline=baseline,
        alerts=alerts,
        abstentions=abstentions,
    )
