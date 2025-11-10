import structlog
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.agent import sdk_log

from routes.api import router as api_router
from routes.lego import router as lego_router

from middlewares.replay_guard import ReplayGuardMiddleware
from middlewares.sdk_audit import SdkAuditMiddleware


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "frontend" / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP ===
    async def _delayed_startup_log():
        await asyncio.sleep(0.3)
        await sdk_log(
            "INFO",
            "LogCenter startup",
            data={"env": settings.ENV, "version": "0.1-dev"},
            status="OK",
        )

    asyncio.create_task(_delayed_startup_log())
    yield
    # === SHUTDOWN ===
    await sdk_log(
        "INFO",
        "LogCenter shutdown",
        data={"env": settings.ENV, "version": "0.1-dev"},
        status="INFO",
    )

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="0.1.5.6-dev", lifespan=lifespan)
    # Structlog setup
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    log = structlog.get_logger()

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.add_middleware(SdkAuditMiddleware)
    app.add_middleware(ReplayGuardMiddleware, ttl_seconds=4)


    app.mount("/design", StaticFiles(directory=STATIC_DIR / "design"), name="design")
    app.mount("/templates/lego", StaticFiles(directory=STATIC_DIR / "templates" / "lego"), name="templates_lego")


    app.include_router(api_router)
    app.include_router(lego_router)

    @app.get("/alive")
    async def alive():
        return {"status": "ok", "env": settings.ENV}

    return app
