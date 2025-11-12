from fastapi import APIRouter, Request
from schemas.log import LogIn, LogOut
from core.agent import sdk_log


router = APIRouter(prefix="/log", tags=["log"])


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
    return res