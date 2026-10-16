import asyncio
import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api import analytics, automation, catalog, model_lab, simulation, stream
from app.api.deps import ProtectiveDenial, gated
from app.bootstrap import Container, build_container
from app.config import Settings
from app.network_api import network_router
from app.security import BodyLimit

API_ROOT = Path(__file__).parents[1]
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def migrate(database_url: str) -> None:
    migration = Config(str(API_ROOT / "alembic.ini"))
    migration.set_main_option("script_location", str(API_ROOT / "migrations"))
    migration.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(migration, "head")


def lifespan_for(c: Container):
    @asynccontextmanager
    async def lifespan(app):
        log_dir = c.database_path.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_handler = RotatingFileHandler(
            log_dir / "application.log", maxBytes=1048576, backupCount=5, encoding="utf-8"
        )
        log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        await asyncio.to_thread(migrate, c.settings.database_url)
        await c.pipeline.start_tasks()
        await c.experiment_jobs.start()
        backup_task = asyncio.create_task(c.backup_worker.run()) if c.backup_worker else None
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
            await c.experiment_jobs.close()
            if c.backup_worker:
                c.backup_worker.stop.set()
                await backup_task
            await c.pipeline.close()
            c.store.engine.dispose()
            for logger, handlers, propagate in previous_logging:
                logger.handlers = handlers
                logger.propagate = propagate
            log_handler.close()

    return lifespan


def create_app(settings: Settings | None = None):
    # Configure logging here, not at import time, so importing the module has no side effects.
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    c = build_container(settings or Settings())
    docs = c.settings.api_docs_enabled
    app = FastAPI(
        title="WiFi Spatial Intelligence API",
        version="0.1.0",
        lifespan=lifespan_for(c),
        docs_url="/docs" if docs else None,
        redoc_url="/redoc" if docs else None,
    )
    app.state.container = c
    app.state.pipeline = c.pipeline
    app.state.store = c.store
    app.state.limiter = c.limiter

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
        # Invalid transitions (pause while stopped) are not security events.
        if isinstance(error, ProtectiveDenial):
            await asyncio.to_thread(c.store.security_denial, "operation.denied")
        return await http_exception_handler(request, error)

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=c.settings.allowed_hosts)
    app.add_middleware(BodyLimit)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=c.settings.origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    app.include_router(network_router(c.store.engine, gated("network.link_diagnostics")))
    for module in (automation, model_lab, analytics):
        app.include_router(module.router)
    app.include_router(catalog.public)
    app.include_router(simulation.router)
    app.include_router(catalog.router)
    app.include_router(stream.router)
    return app
