"""Health, honest capability declarations, virtual layout and governance status."""

from fastapi import APIRouter

from app.api.deps import ContainerDep, protected, require_capability
from app.capabilities import CapabilityCatalog, catalog
from app.domain.acquisition import ROOM_HEIGHT_M, ROOM_WIDTH_M, VIRTUAL_SENSOR_POSITIONS

public = APIRouter()
router = APIRouter(dependencies=protected)


@public.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "0.1.0", "mode": "simulation-only"}


@router.get("/api/v1/system/status")
async def status(c: ContainerDep):
    # Operational state stays readable in every profile (dashboard login uses it).
    return c.pipeline.status()


@router.get("/api/v1/providers")
def providers(c: ContainerDep):
    return [
        {"id": "synthetic-native", "status": "IMPLEMENTED_SYNTHETIC"},
        {
            "id": "RUVIEW_STREAM",
            "status": "INTEGRATED_LEGACY" if c.settings.legacy_lab_enabled else "BLOCKED",
        },
        {"id": "ESP32_CSI", "status": "BLOCKED", "reason": "no physical hardware"},
        {"id": "MULTIMODAL", "status": "PLANNED"},
    ]


@router.get("/api/v1/features")
def features():
    # Synthetic implementations only; real sensing claims live in /capabilities evidence.
    return [
        {"id": name, "status": "IMPLEMENTED_SYNTHETIC"}
        for name in [
            "simulation",
            "dashboard",
            "observatory",
            "history",
            "sensors",
            "analytics",
            "replay",
            "model_lab_baseline",
            "automation_dry_run",
        ]
    ] + [
        {"id": name, "status": "PLANNED"}
        for name in ["vitals", "pose", "sleep", "homecore", "metaharness"]
    ]


@router.get("/api/v1/capabilities", response_model=CapabilityCatalog)
def capabilities(c: ContainerDep):
    return catalog(c.settings.capability_profile)


@router.get("/api/v1/rooms")
def rooms():
    return [
        {
            "id": "living-room",
            "name": "Virtual laboratory",
            "width_m": ROOM_WIDTH_M,
            "height_m": ROOM_HEIGHT_M,
            "evidence_level": "L0_SYNTHETIC",
        }
    ]


@router.get("/api/v1/sensors", dependencies=[require_capability("spatial.presence")])
def sensors(c: ContainerDep):
    pipeline = c.pipeline
    connected = pipeline.source == "synthetic-native" and pipeline.provider.connected
    return [
        {
            "id": f"virtual-{i + 1}",
            "source_type": "SIMULATED",
            "virtual": True,
            "position_m": position,
            "connected": connected,
            "firmware": None,
            "signal_quality": None,
            "evidence_level": "L0_SYNTHETIC",
        }
        for i, position in enumerate(VIRTUAL_SENSOR_POSITIONS)
    ]


@router.get("/api/v1/occupancy", dependencies=[require_capability("spatial.presence")])
def occupancy(c: ContainerDep):
    return {
        "measurement": c.pipeline.latest,
        "interpretation": "upstream estimates over synthetic signals"
        if c.pipeline.source == "RUVIEW_STREAM"
        else "synthetic ground truth",
    }


@router.get("/api/v1/models")
def models():
    return {"items": [], "reason": "no inference model installed or validated"}


@router.get("/api/v1/validation")
def validation():
    return {
        "real_data_validated": False,
        "evidence_level": "L0_SYNTHETIC",
        "inference_executed": False,
    }


@router.get("/api/v1/governance/status")
def governance(c: ContainerDep):
    return {
        "security_audit": c.store.security_audits(),
        "backup": c.backup_worker.status() if c.backup_worker else {"enabled": False},
        "real_sensing_enabled": False,
        "consent_records": [],
        "retention_events": c.settings.retention_events,
        "authentication": "loopback development bearer token",
        "clinical_validation": False,
        "audit": c.store.audits(),
    }
