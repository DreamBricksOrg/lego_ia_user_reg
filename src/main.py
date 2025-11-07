import structlog
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings

from routes.api import router as api_router
from routes.registrations import router as reg_router
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.skyn import router as skyn_router

from middlewares.replay_guard import ReplayGuardMiddleware


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "frontend" / "static"

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

    app.add_middleware(ReplayGuardMiddleware, ttl_seconds=4)


    app.mount("/design", StaticFiles(directory=STATIC_DIR / "design"), name="design")
    app.mount("/templates", StaticFiles(directory=STATIC_DIR / "templates"), name="templates")
    app.mount("/templates/admin", StaticFiles(directory=STATIC_DIR / "templates" / "admin"), name="templates_admin")
    app.mount("/templates/skyn", StaticFiles(directory=STATIC_DIR / "templates" / "skyn"), name="templates_skyn")


    app.include_router(api_router)
    app.include_router(reg_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(skyn_router)

    @app.get("/alive")
    async def alive():
        return {"status": "ok", "env": settings.ENV}

    return app
