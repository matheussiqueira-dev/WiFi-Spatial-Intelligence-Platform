"""Channel congestion heuristic over aggregated passive surveys. Advice only: no router change."""

from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Sequence

from app.network_contracts import (
    Advice,
    Band,
    BandPlan,
    ChannelOccupancy,
    ChannelPlan,
    ChannelScore,
    ChannelSurvey,
)

# 20 MHz channels usable without DFS radar detection in most regulatory domains.
CANDIDATES: dict[Band, tuple[int, ...]] = {
    "2.4GHz": (1, 6, 11),
    "5GHz": (36, 40, 44, 48, 149, 153, 157, 161, 165),
}
CHANGE_MARGIN = 0.5
LIMITATIONS = [
    "Heurística sobre a lista de redes que o Windows já obteve; não é medição de espectro.",
    "O próprio roteador (e nós de mesh) aparece na varredura; desconta-se uma rede "
    "no canal atual, mas outros nós e o rádio da outra banda do mesmo roteador "
    "contam como vizinhos.",
    "Em 5 GHz considera-se sobreposição pelo bloco de 80 MHz; larguras reais não são lidas.",
    "6 GHz e canais DFS não recebem recomendação. Nenhuma configuração é alterada.",
]


def overlap(band: Band, candidate: int, observed: int) -> float:
    if band == "2.4GHz":
        return max(0.0, 1 - abs(candidate - observed) / 5)
    if candidate == observed:
        return 1.0
    return 0.5 if block_80(candidate) == block_80(observed) else 0.0


def block_80(channel: int) -> int:
    if 36 <= channel <= 64:
        return (channel - 36) // 16
    if 100 <= channel <= 144:
        return 2 + (channel - 100) // 16
    if 149 <= channel <= 161:
        return 100
    return 1000 + channel


def plan(
    surveys: Sequence[ChannelSurvey],
    current_channel: int | None,
    start: datetime,
    end: datetime,
    location: str | None,
) -> ChannelPlan:
    valid = sorted(
        (row for row in surveys if row.collector_error is None),
        key=lambda row: (row.timestamp, str(row.survey_id)),
    )
    weights: dict[tuple[Band, int], list[float]] = defaultdict(list)
    counts: dict[tuple[Band, int], list[float]] = defaultdict(list)
    for survey in valid:
        seen = set()
        for row in survey.channels:
            key = (row.band, row.channel)
            own = row.channel == current_channel and row.band == band_of(row.channel)
            count = row.ap_count - own
            utilization = (row.utilization_percent or 0) / 100
            seen.add(key)
            counts[key].append(count)
            weights[key].append(count * row.strongest_signal_percent / 100 + utilization)
        for key in counts.keys() - seen:
            counts[key].append(0)
            weights[key].append(0)
    # Channels first seen in later surveys were absent (zero) in earlier ones.
    for key in counts:
        missing = len(valid) - len(counts[key])
        counts[key][:0] = [0] * missing
        weights[key][:0] = [0] * missing
    pressure = {key: mean(values) for key, values in weights.items()}
    latest = valid[-1].channels if valid else []
    bands: list[BandPlan] = []
    for band in ("2.4GHz", "5GHz", "6GHz"):
        observed = sorted((row for row in latest if row.band == band), key=lambda row: row.channel)
        current = current_channel if current_channel and band_of(current_channel) == band else None
        if not observed and current is None and all(key[0] != band for key in pressure):
            continue

        def score(channel: int, band: Band = band) -> float:
            return round(
                sum(
                    overlap(band, channel, key[1]) * value
                    for key, value in pressure.items()
                    if key[0] == band
                ),
                3,
            )

        if band not in CANDIDATES:
            bands.append(
                BandPlan(
                    band=band,
                    observed=list(observed),
                    candidates=[],
                    current_channel=current,
                    current_score=None,
                    recommended_channel=None,
                    advice="NOT_MODELED",
                )
            )
            continue
        candidates = sorted(
            (
                ChannelScore(
                    channel=channel,
                    observed_ap_count=round(mean(counts.get((band, channel), [0])), 2),
                    interference_score=score(channel),
                )
                for channel in CANDIDATES[band]
            ),
            key=lambda row: (row.interference_score, row.channel),
        )
        best = candidates[0]
        current_score = score(current) if current is not None and valid else None
        advice: Advice
        if current is None or current_score is None:
            advice, recommended = "NO_CURRENT", best.channel if valid else None
        elif current_score - best.interference_score >= CHANGE_MARGIN:
            advice, recommended = "CONSIDER_CHANGE", best.channel
        else:
            advice, recommended = "KEEP", current
        bands.append(
            BandPlan(
                band=band,
                observed=list(observed),
                candidates=candidates if valid else [],
                current_channel=current,
                current_score=current_score,
                recommended_channel=recommended,
                advice=advice,
            )
        )
    return ChannelPlan(
        start=start,
        end=end,
        location=location,
        surveys=len(valid),
        failed_surveys=len(surveys) - len(valid),
        last_survey_at=valid[-1].timestamp if valid else None,
        bands=bands,
        limitations=LIMITATIONS,
    )


def band_of(channel: int) -> Band:
    # Without the band field, low numbers are ambiguous with 6 GHz; prefer the common case.
    return "2.4GHz" if channel <= 14 else "5GHz"


def aggregate(networks: Sequence[dict]) -> list[ChannelOccupancy]:
    """Collapse per-BSSID readings (already stripped of identity) into per-channel totals."""
    groups: dict[tuple[Band, int], list[dict]] = defaultdict(list)
    for row in networks:
        groups[(row["band"], row["channel"])].append(row)
    result = []
    for (band, channel), rows in sorted(groups.items())[:64]:
        utilization = [
            row["utilization_percent"] for row in rows if row.get("utilization_percent") is not None
        ]
        result.append(
            ChannelOccupancy(
                band=band,
                channel=channel,
                ap_count=min(len(rows), 500),
                strongest_signal_percent=max(row["signal_percent"] for row in rows),
                utilization_percent=max(utilization) if utilization else None,
            )
        )
    return result
