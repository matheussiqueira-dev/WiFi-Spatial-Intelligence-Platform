"""Capability catalog: what exists, what evidence it can produce and its regulatory framing.

Declarative only. Tags are working hypotheses for later review, not legal advice
(docs/PROJECT_MASTER_PLAN.md section 0A).
"""

from typing import Literal

from app.contracts import StrictModel

Group = Literal["A", "B", "C", "D"]
Status = Literal[
    "UNVERIFIED",
    "PARTIAL",
    "IMPLEMENTED_SYNTHETIC",
    "IMPLEMENTED_LIVE",
    "INTEGRATED_LEGACY",
    "VALIDATED_REAL_DATA",
    "PLANNED",
    "BLOCKED",
]
Evidence = Literal[
    "L0_SYNTHETIC", "L1_RECORDED_UNVALIDATED", "L2_LIVE_UNVALIDATED", "L3_REFERENCE_VALIDATED"
]
Regulatory = Literal["NONE", "LGPD_PERSONAL", "LGPD_SENSITIVE", "ANATEL_RADIO", "ANVISA_SAMD"]
Profile = Literal["lab", "commercial-br"]


class Capability(StrictModel):
    id: str
    name: str
    group: Group
    status: Status
    evidence_ceiling: Evidence | None
    regulatory: list[Regulatory]
    requires_hardware: bool
    requires_consent: bool
    profiles: list[Profile]
    endpoint: str | None
    note: str


class CapabilityState(Capability):
    enabled: bool


class CapabilityCatalog(StrictModel):
    profile: Profile
    disclaimer: str
    capabilities: list[CapabilityState]


CATALOG: tuple[Capability, ...] = (
    Capability(
        id="network.link_diagnostics",
        name="Diagnóstico do enlace Wi-Fi do computador",
        group="A",
        status="IMPLEMENTED_LIVE",
        evidence_ceiling="L2_LIVE_UNVALIDATED",
        regulatory=["NONE"],
        requires_hardware=False,
        requires_consent=False,
        profiles=["lab", "commercial-br"],
        endpoint="/api/v1/network/report",
        note="Sinal, canal, taxas e sondas ICMP ao gateway privado; sem SSID/BSSID.",
    ),
    Capability(
        id="network.location_comparison",
        name="Comparação de pontos do ambiente",
        group="A",
        status="IMPLEMENTED_LIVE",
        evidence_ceiling="L2_LIVE_UNVALIDATED",
        regulatory=["NONE"],
        requires_hardware=False,
        requires_consent=False,
        profiles=["lab", "commercial-br"],
        endpoint="/api/v1/network/report",
        note="Ponto nomeado manualmente pelo operador; não há localização por RF.",
    ),
    Capability(
        id="network.channel_plan",
        name="Ocupação de canais e recomendação de canal",
        group="A",
        status="IMPLEMENTED_LIVE",
        evidence_ceiling="L2_LIVE_UNVALIDATED",
        regulatory=["NONE"],
        requires_hardware=False,
        requires_consent=False,
        profiles=["lab", "commercial-br"],
        endpoint="/api/v1/network/channel-plan",
        note="Varredura passiva já feita pelo Windows; só agregados por canal saem do host.",
    ),
    Capability(
        id="network.degradation_alerts",
        name="Tendência do enlace e alertas de degradação",
        group="A",
        status="IMPLEMENTED_LIVE",
        evidence_ceiling="L2_LIVE_UNVALIDATED",
        regulatory=["NONE"],
        requires_hardware=False,
        requires_consent=False,
        profiles=["lab", "commercial-br"],
        endpoint="/api/v1/network/health",
        note="Última hora contra a linha de base do mesmo ponto; consultivo, sem disparo.",
    ),
    Capability(
        id="network.alert_webhook",
        name="Webhook local assinado para alertas de rede",
        group="A",
        status="IMPLEMENTED_LIVE",
        evidence_ceiling="L2_LIVE_UNVALIDATED",
        regulatory=["NONE"],
        requires_hardware=False,
        requires_consent=False,
        profiles=["lab", "commercial-br"],
        endpoint="/api/v1/network/webhook",
        note="Só IP de loopback/rede privada, HMAC-SHA256, sem redirect; notifica, não age.",
    ),
    Capability(
        id="hardware.csi_frame_protocol",
        name="Protocolo SWF1 de quadros CSI (ESP32-S3)",
        group="B",
        status="IMPLEMENTED_SYNTHETIC",
        evidence_ceiling="L0_SYNTHETIC",
        regulatory=["ANATEL_RADIO"],
        requires_hardware=True,
        requires_consent=False,
        profiles=["lab"],
        endpoint=None,
        note="Parser autenticado e simulador de transporte; placa real NOT_TESTED e recusada.",
    ),
    Capability(
        id="spatial.presence",
        name="Presença e movimento",
        group="B",
        status="IMPLEMENTED_SYNTHETIC",
        evidence_ceiling="L0_SYNTHETIC",
        regulatory=["LGPD_PERSONAL", "ANATEL_RADIO"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint="/api/v1/events",
        note="Sensores virtuais; dado real exige CSI e consentimento dos ocupantes.",
    ),
    Capability(
        id="spatial.occupancy_analytics",
        name="Ocupação por zona, permanência e transições",
        group="B",
        status="IMPLEMENTED_SYNTHETIC",
        evidence_ceiling="L0_SYNTHETIC",
        regulatory=["LGPD_PERSONAL"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint="/api/v1/analytics",
        note="Analytics sobre eventos persistidos; hoje somente sintéticos.",
    ),
    Capability(
        id="spatial.activity_baseline",
        name="Classificador baseline de atividade",
        group="B",
        status="IMPLEMENTED_SYNTHETIC",
        evidence_ceiling="L0_SYNTHETIC",
        regulatory=["LGPD_PERSONAL"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint="/api/v1/model-lab/jobs",
        note="Treino e avaliação em dataset sintético; não é acurácia real.",
    ),
    Capability(
        id="automation.dry_run_rules",
        name="Regras locais de automação em dry-run",
        group="B",
        status="IMPLEMENTED_SYNTHETIC",
        evidence_ceiling="L0_SYNTHETIC",
        regulatory=["LGPD_PERSONAL"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint="/api/v1/automation/rules",
        note="Decisões sobre eventos de presença/ocupação; nenhuma ação é despachada.",
    ),
    Capability(
        id="spatial.rf_fingerprint",
        name="Impressão RF e anomalia do ambiente",
        group="B",
        status="PLANNED",
        evidence_ceiling=None,
        regulatory=["ANATEL_RADIO"],
        requires_hardware=True,
        requires_consent=False,
        profiles=["lab"],
        endpoint=None,
        note="Depende de CSI; não identifica qual objeto ou pessoa mudou.",
    ),
    Capability(
        id="health.respiration",
        name="Frequência respiratória",
        group="C",
        status="PLANNED",
        evidence_ceiling=None,
        regulatory=["LGPD_SENSITIVE", "ANVISA_SAMD"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint=None,
        note="Pesquisa não diagnóstica; sem alegação clínica.",
    ),
    Capability(
        id="health.heart_rate",
        name="Frequência cardíaca",
        group="C",
        status="PLANNED",
        evidence_ceiling=None,
        regulatory=["LGPD_SENSITIVE", "ANVISA_SAMD"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint=None,
        note="Pesquisa não diagnóstica; sem alegação clínica.",
    ),
    Capability(
        id="safety.fall_detection",
        name="Detecção de queda",
        group="C",
        status="PLANNED",
        evidence_ceiling=None,
        regulatory=["LGPD_SENSITIVE", "ANVISA_SAMD"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint=None,
        note="Não é alerta de segurança certificado.",
    ),
    Capability(
        id="health.sleep",
        name="Sono e triagem de apneia",
        group="C",
        status="PLANNED",
        evidence_ceiling=None,
        regulatory=["LGPD_SENSITIVE", "ANVISA_SAMD"],
        requires_hardware=True,
        requires_consent=True,
        profiles=["lab"],
        endpoint=None,
        note="Pesquisa não diagnóstica.",
    ),
    Capability(
        id="identity.rf_reidentification",
        name="Reidentificação de pessoas por RF",
        group="D",
        status="BLOCKED",
        evidence_ceiling=None,
        regulatory=["LGPD_SENSITIVE"],
        requires_hardware=True,
        requires_consent=True,
        profiles=[],
        endpoint=None,
        note="Bloqueada pelo princípio 5; reabre apenas por decisão explícita do proprietário.",
    ),
)

DISCLAIMER = (
    "Enquadramento regulatório preliminar para planejamento; não é parecer jurídico "
    "nem certificação. Revisar com especialista antes de comercializar."
)


def catalog(profile: Profile) -> CapabilityCatalog:
    return CapabilityCatalog(
        profile=profile,
        disclaimer=DISCLAIMER,
        capabilities=[
            CapabilityState(
                **item.model_dump(),
                enabled=profile in item.profiles and item.status not in {"PLANNED", "BLOCKED"},
            )
            for item in CATALOG
        ],
    )


def declared(capability_id: str) -> bool:
    return any(item.id == capability_id for item in CATALOG)


def is_enabled(capability_id: str, profile: Profile) -> bool:
    return any(item.id == capability_id and item.enabled for item in catalog(profile).capabilities)
