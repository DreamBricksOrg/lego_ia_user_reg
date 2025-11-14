from fastapi import APIRouter, Request
from schemas.log import LogIn, LogOut
from core.agent import sdk_log
from core.config import settings
from utils.log_sender import LogSender, LOG_DIR
import os


router = APIRouter(prefix="/log", tags=["log"])

# Garante diretório de logs e instancia logger CSV (desacoplado)
os.makedirs(LOG_DIR, exist_ok=True)
_csv_logger = LogSender(log_api="https://dbutils.ddns.net", project_id="6914cbb1de25f74417212f41")


@router.post("/create-log", response_model=LogOut)
async def create_log(body: LogIn, request: Request):
    enriched = dict(body.data or {})
    enriched.update({
        "sessionId": body.sessionId,
        "userId": body.userId,
        "client": {
            "ip": request.client.host if request.client else None,
            "ua": request.headers.get("User-Agent"),
            "ref": request.headers.get("Referer"),
        },
        "path": request.url.path,
    })
    res = await sdk_log(
        level=body.level,
        message=body.message,
        tags=body.tags or [],
        data=enriched,
    )
    try:
        status = body.message
        additional = ""
        _csv_logger.log(status=status, additional=additional)
    except Exception:
        pass

    return res