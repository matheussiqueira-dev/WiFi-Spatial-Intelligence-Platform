import asyncio
import hmac
import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.websockets import WebSocketDisconnect

from app.adapters.history import SqliteHistoryRepository
from app.analytics import AnalyticsQuery, aggregate, csv_report, replay
from app.application.experiment_jobs import ExperimentJobs
from app.application.model_lab import ExperimentRequest, ModelLab
from app.application.read_history import ReadHistory
from app.config import Settings
from app.contracts import SimulationConfig, SourceSelection
from app.lab_contracts import ExperimentResult
from app.network_api import network_router
from app.pipeline import Pipeline
from app.ports.history import HistorySelection
from app.recurring_backup import RecurringBackup
from app.rule_contracts import RuleRequest
from app.security import BodyLimit, LocalLimiter
from app.storage import Store

bearer = HTTPBearer(auto_error=False)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    if not settings.database_url.startswith("sqlite:///"):
        raise ValueError("only local SQLite is supported in phase 1")
    db_path = settings.database_url.removeprefix("sqlite:///")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    store = Store(settings.database_url, settings.retention_events)
    pipeline = Pipeline(store, settings)
    model_lock = asyncio.Lock()
    model_lab = ModelLab(store, Path(db_path).parent / "model-lab")
    experiment_jobs = ExperimentJobs(model_lab, model_lock)
    limiter = LocalLimiter(
        {
            "auth": settings.rate_auth,
            "write": settings.rate_write,
            "read": settings.rate_read,
            "stream": settings.rate_stream,
        }
    )
    backup_worker = (
        RecurringBackup(
            Path(db_path),
            Path(settings.backup_destination),
            Path(__file__).parents[3],
            settings.backup_interval_seconds,
        )
        if settings.backup_enabled
        else None
    )

    @asynccontextmanager
    async def lifespan(app):
        log_dir = Path(db_path).parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_handler = RotatingFileHandler(
            log_dir / "application.log", maxBytes=1048576, backupCount=5, encoding="utf-8"
        )
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        migration = Config(str(Path(__file__).parents[1] / "alembic.ini"))
        migration.set_main_option("script_location", str(Path(__file__).parents[1] / "migrations"))
        migration.set_main_option("sqlalchemy.url", settings.database_url)
        await asyncio.to_thread(command.upgrade, migration, "head")
        await pipeline.start_tasks()
        await experiment_jobs.start()
        backup_task = asyncio.create_task(backup_worker.run()) if backup_worker else None
        loggers = [
            logging.getLogger(name) for name in ("spatial", "uvicorn.access", "uvicorn.error")
        ]
        previous_logging = [(logger, logger.handlers[:], logger.propagate) for logger in loggers]
        for logger in loggers:
            logger.handlers = [log_handler]
            logger.propagate = False
        try:
            yield
        finally:
            await experiment_jobs.close()
            if backup_worker:
                backup_worker.stop.set()
                await backup_task
            await pipeline.close()
            store.engine.dispose()
            for logger, handlers, propagate in previous_logging:
                logger.handlers = handlers
                logger.propagate = propagate
            log_handler.close()

    app = FastAPI(title="WiFi Spatial Intelligence API", version="0.1.0", lifespan=lifespan)
    app.state.pipeline = pipeline
    app.state.store = store
    app.state.limiter = limiter

    @app.exception_handler(Exception)
    async def unexpected_http_error(request: Request, error: Exception) -> JSONResponse:
        # Do not log URL, body, headers, or exception text, which may contain secrets.
        logging.getLogger("spatial.api").error("http failure type=%s", type(error).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "internal service error"},
            headers={"Cache-Control": "no-store"},
        )

    @app.exception_handler(HTTPException)
    async def record_operation_denial(request, error):
        if error.status_code == 409:
            await asyncio.to_thread(store.security_denial, "operation.denied")
        return await http_exception_handler(request, error)

    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver", "api"]
    )
    app.add_middleware(BodyLimit)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    async def authorize(
        request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
    ):
        origin = request.headers.get("origin")
        if origin and origin not in settings.origins:
            await asyncio.to_thread(store.security_denial, "origin.denied")
            raise HTTPException(403, "origin not allowed")
        peer = request.client.host if request.client else "local"
        if not credentials or not hmac.compare_digest(
            credentials.credentials.encode("utf-8"), settings.token.encode("utf-8")
        ):
            retry = limiter.check("auth", peer)
            await asyncio.to_thread(
                store.security_denial, "rate.denied" if retry else "auth.denied"
            )
            if retry:
                raise HTTPException(
                    429, "request limit reached", headers={"Retry-After": str(retry)}
                )
            raise HTTPException(401, "valid local development token required")
        category = "read" if request.method == "GET" else "write"
        retry = limiter.check(category, peer)
        if retry:
            await asyncio.to_thread(store.security_denial, "rate.denied")
            raise HTTPException(429, "request limit reached", headers={"Retry-After": str(retry)})

    protected = [Depends(authorize)]
    app.include_router(network_router(store.engine, protected))
    history_reader = ReadHistory(SqliteHistoryRepository(store))
    rules_lock = asyncio.Lock()

    @app.post("/api/v1/automation/rules", dependencies=protected)
    async def create_rule(rule: RuleRequest):
        async with rules_lock:
            try:
                return await asyncio.to_thread(store.create_rule, rule.model_dump())
            except ValueError as error:
                raise HTTPException(422, str(error)) from error

    @app.get("/api/v1/automation/rules", dependencies=protected)
    def get_rules():
        return store.local_rules()

    @app.post("/api/v1/automation/rules/{identifier}/revoke", dependencies=protected)
    async def revoke_rule(identifier: str):
        # Same lock as ingestion: no in-flight decision can commit after revocation returns.
        async with pipeline.control_lock:
            await pipeline.queue.join()
            if not await asyncio.to_thread(store.revoke_rule, identifier):
                raise HTTPException(404, "rule not found")
        return {"revoked": True, "mode": "DRY_RUN"}

    @app.get("/api/v1/automation/decisions", dependencies=protected)
    def get_decisions(limit: int = Query(20, ge=1, le=200), offset: int = Query(0, ge=0, le=1000)):
        return store.rule_decisions(limit, offset)

    @app.post("/api/v1/model-lab/jobs", dependencies=protected)
    async def submit_experiment(query: ExperimentRequest):
        try:
            return await experiment_jobs.submit(query)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    @app.get("/api/v1/model-lab/jobs/{identifier}", dependencies=protected)
    def get_job(identifier: str):
        if experiment_jobs.last_error:
            raise HTTPException(503, "job status persistence unavailable")
        job = store.job(identifier)
        if job is None:
            raise HTTPException(404, "job not found")
        return job

    @app.post("/api/v1/model-lab/jobs/{identifier}/cancel", dependencies=protected)
    def cancel_job(identifier: str):
        if not experiment_jobs.cancel(identifier):
            raise HTTPException(409, "job is already terminal or absent")
        return {"cancel_requested": True}

    @app.post("/api/v1/model-lab/runs", dependencies=protected, response_model=ExperimentResult)
    async def run_experiment(query: ExperimentRequest):
        if model_lock.locked():
            raise HTTPException(409, "one experiment at a time")
        async with model_lock:
            try:
                return await asyncio.to_thread(model_lab.execute, query)
            except ValueError as error:
                raise HTTPException(422, str(error)) from error

    @app.get("/api/v1/model-lab/runs", dependencies=protected)
    def list_experiments(
        limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=100)
    ):
        return store.model_runs(limit, offset)

    @app.get(
        "/api/v1/model-lab/runs/{identifier}",
        dependencies=protected,
        response_model=ExperimentResult,
    )
    def get_experiment(identifier: str):
        result = store.model_run(identifier)
        if result is None:
            raise HTTPException(404, "experiment not found")
        return result

    def analysis_rows(query):
        try:
            return history_reader.execute(
                HistorySelection(
                    query.start, query.end, query.source_id, query.scenario, query.segment_id
                )
            )
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.get("/api/v1/analytics", dependencies=protected)
    def analytics(query: Annotated[AnalyticsQuery, Query()]):
        return aggregate(analysis_rows(query), query)

    @app.get("/api/v1/analytics/replay", dependencies=protected)
    def analytics_replay(query: Annotated[AnalyticsQuery, Query()]):
        return replay(analysis_rows(query), query)

    @app.get("/api/v1/analytics/export.csv", dependencies=protected)
    def analytics_export(query: Annotated[AnalyticsQuery, Query()]):
        return Response(
            csv_report(aggregate(analysis_rows(query), query)),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="synthetic-analytics.csv"'},
        )

    @app.post("/api/v1/analytics/reports", dependencies=protected)
    def save_analytics(query: AnalyticsQuery):
        report = aggregate(analysis_rows(query), query)
        return {"id": store.save_report(report), "evidence_level": "L0_SYNTHETIC"}

    @app.get("/api/v1/analytics/reports", dependencies=protected)
    def list_reports(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=10000)):
        return store.reports(limit, offset)

    @app.get("/api/v1/analytics/reports/{identifier}", dependencies=protected)
    def get_report(identifier: str):
        result = store.report(identifier)
        if result is None:
            raise HTTPException(404, "report not found")
        return result

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok", "version": "0.1.0", "mode": "simulation-only"}

    @app.get("/api/v1/system/status", dependencies=protected)
    def status():
        return pipeline.status()

    @app.get("/api/v1/providers", dependencies=protected)
    def providers():
        return [
            {"id": "synthetic-native", "status": "IMPLEMENTED_SYNTHETIC"},
            {
                "id": "RUVIEW_STREAM",
                "status": "INTEGRATED_LEGACY" if settings.legacy_lab_enabled else "BLOCKED",
            },
            {"id": "ESP32_CSI", "status": "BLOCKED", "reason": "no physical hardware"},
            {"id": "MULTIMODAL", "status": "PLANNED"},
        ]

    @app.get("/api/v1/features", dependencies=protected)
    def features():
        return [
            {"id": name, "status": "IMPLEMENTED_SYNTHETIC"}
            for name in ["simulation", "dashboard", "observatory", "history", "sensors"]
        ] + [
            {"id": name, "status": "PLANNED"}
            for name in ["vitals", "pose", "sleep", "training", "homecore", "metaharness"]
        ]

    @app.get("/api/v1/rooms", dependencies=protected)
    def rooms():
        return [
            {
                "id": "living-room",
                "name": "Virtual laboratory",
                "width_m": 8,
                "height_m": 6,
                "evidence_level": "L0_SYNTHETIC",
            }
        ]

    @app.get("/api/v1/sensors", dependencies=protected)
    def sensors():
        return [
            {
                "id": f"virtual-{i + 1}",
                "source_type": "SIMULATED",
                "virtual": True,
                "position_m": position,
                "connected": pipeline.source == "synthetic-native" and pipeline.provider.connected,
                "firmware": None,
                "signal_quality": None,
                "evidence_level": "L0_SYNTHETIC",
            }
            for i, position in enumerate([(0, 0), (4, 0), (8, 0), (0, 6), (4, 6), (8, 6)])
        ]

    @app.get("/api/v1/events", dependencies=protected)
    async def events(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0, le=100000)):
        return await asyncio.to_thread(store.history, limit, offset)

    @app.delete("/api/v1/events/synthetic", dependencies=protected)
    async def delete_events():
        try:
            await pipeline.delete_history()
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        return {"deleted": "L0_SYNTHETIC", "audit_preserved": True}

    @app.get("/api/v1/occupancy", dependencies=protected)
    def occupancy():
        return {
            "measurement": pipeline.latest,
            "interpretation": "upstream estimates over synthetic signals"
            if pipeline.source == "RUVIEW_STREAM"
            else "synthetic ground truth",
        }

    @app.get("/api/v1/models", dependencies=protected)
    def models():
        return {"items": [], "reason": "no inference model installed or validated"}

    @app.get("/api/v1/validation", dependencies=protected)
    def validation():
        return {
            "real_data_validated": False,
            "evidence_level": "L0_SYNTHETIC",
            "inference_executed": False,
        }

    @app.get("/api/v1/governance/status", dependencies=protected)
    def governance():
        return {
            "security_audit": store.security_audits(),
            "backup": backup_worker.status() if backup_worker else {"enabled": False},
            "real_sensing_enabled": False,
            "consent_records": [],
            "retention_events": settings.retention_events,
            "authentication": "loopback development bearer token",
            "clinical_validation": False,
            "audit": store.audits(),
        }

    @app.get("/api/v1/simulation/scenarios", dependencies=protected)
    def scenarios():
        return [
            "empty",
            "stationary",
            "walking",
            "entering",
            "leaving",
            "interference",
            "packet_loss",
            "disconnect",
        ]

    @app.post("/api/v1/simulation/start", dependencies=protected)
    async def start(config: SimulationConfig):
        try:
            await pipeline.control("start", config)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        return pipeline.status()

    @app.post("/api/v1/sources/select", dependencies=protected)
    async def select_source(selection: SourceSelection):
        try:
            await pipeline.select_source(selection.source)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        return pipeline.status()

    @app.post("/api/v1/simulation/{action}", dependencies=protected)
    async def control(action: str):
        if action not in {"pause", "resume", "stop", "reset"}:
            raise HTTPException(404, "unknown simulation action")
        try:
            await pipeline.control(action)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        return pipeline.status()

    handshakes: set[object] = set()

    @app.websocket("/api/v1/stream")
    async def stream(ws: WebSocket):
        if ws.headers.get("origin") not in settings.origins:
            await asyncio.to_thread(store.security_denial, "ws.origin_denied")
            await ws.close(code=1008)
            return
        # Pending handshakes hold a slot so the cap also bounds unauthenticated sockets.
        if len(pipeline.subscribers) + len(handshakes) >= 8:
            await asyncio.to_thread(store.security_denial, "ws.limit")
            await ws.close(code=1013)
            return
        peer = ws.client.host if ws.client else "local"
        # Legitimate reconnects use their own budget; "auth" counts only failed tokens.
        if limiter.check("stream", peer):
            await asyncio.to_thread(store.security_denial, "ws.rate_denied")
            await ws.close(code=1013)
            return
        queue = asyncio.Queue(maxsize=16)
        handshake = object()
        handshakes.add(handshake)
        receiver = None
        try:
            await ws.accept()
            auth = await asyncio.wait_for(
                ws.receive_json(), timeout=settings.ws_auth_timeout_seconds
            )
            if (
                not isinstance(auth, dict)
                or not isinstance(auth.get("token"), str)
                or not hmac.compare_digest(
                    auth["token"].encode("utf-8"), settings.token.encode("utf-8")
                )
            ):
                limiter.check("auth", peer)
                await asyncio.to_thread(store.security_denial, "ws.auth_denied")
                await ws.close(code=1008)
                return
            handshakes.discard(handshake)
            pipeline.subscribers.add(queue)
            await ws.send_json({"type": "status", "data": pipeline.status()})

            async def receive_disconnect():
                while True:
                    message = await ws.receive()
                    if message["type"] == "websocket.disconnect":
                        return

            receiver = asyncio.create_task(receive_disconnect())
            while not receiver.done():
                pending = asyncio.create_task(queue.get())
                try:
                    done, _ = await asyncio.wait(
                        {pending, receiver}, timeout=2, return_when=asyncio.FIRST_COMPLETED
                    )
                    if receiver in done:
                        break
                    if pending in done:
                        await asyncio.wait_for(
                            ws.send_json({"type": "event", "data": pending.result()}), 5
                        )
                    else:
                        await asyncio.wait_for(
                            ws.send_json({"type": "status", "data": pipeline.status()}), 5
                        )
                finally:
                    pending.cancel()
                    await asyncio.gather(pending, return_exceptions=True)
        except TimeoutError:
            if receiver is None:
                limiter.check("auth", peer)
                await asyncio.to_thread(store.security_denial, "ws.timeout")
                await ws.close(code=1008)
        except (ValueError, KeyError):
            # Malformed JSON or a binary first frame is a failed authentication attempt.
            limiter.check("auth", peer)
            await asyncio.to_thread(store.security_denial, "ws.auth_denied")
            await ws.close(code=1008)
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            handshakes.discard(handshake)
            pipeline.subscribers.discard(queue)
            if receiver:
                receiver.cancel()
                await asyncio.gather(receiver, return_exceptions=True)

    return app
