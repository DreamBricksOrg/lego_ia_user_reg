from __future__ import annotations

import asyncio
from fastapi import APIRouter, HTTPException

from services.totem_service import (
    create_session, get_session, set_crm_result, mark_authorized, advance, init_qr_for_session
)
from schemas.totem import (
    QRInitRequest, TermsRequest, QRInitResponse, StartResponse, CheckWithSession, ContinueRequest, NextRequest
)
from services.crm_service import CRMService
from utils.shortener_client import create_short_link
from schemas.crm import CheckRequest, UpsertRequest
from utils.udp_sender import UDPSender
from core.config import settings


router = APIRouter(prefix="/totem", tags=["totem"])


# instância de envio UDP
udp_sender = UDPSender(port=settings.UDP_PORT)
serial_lock = asyncio.Lock()


@router.post("/session/start", response_model=StartResponse)
async def start_session():
    s = await create_session()
    return StartResponse(sessionId=s["sessionId"], step=s["step"])

@router.get("/session/{session_id}")
async def read_session(session_id: str):
    s = await get_session(session_id)
    if s is None:
        raise HTTPException(404, "session not found")
    return s


@router.post("/session/terms")
async def accept_terms(body: TermsRequest):
    if not body.accepted:
        raise HTTPException(400, "terms not accepted")
    return await advance(body.sessionId, "check")


@router.post("/qrcode/init", response_model=QRInitResponse)
async def qrcode_init(body: QRInitRequest):
    if body.sessionId:
        s = await get_session(body.sessionId)
        if s is None:
            s = await create_session()
    else:
        s = await create_session()
    s = await init_qr_for_session(s["sessionId"])
    qr = s.get("qr", {})
    return QRInitResponse(
        sessionId=s["sessionId"],
        short_url=qr.get("short_url"),
        qr_png=qr.get("qr_png"),
        qr_svg=qr.get("qr_svg"),
    )


@router.get("/qrcode/create")
async def qrcode_create(
    long_url: str,
    name: str | None = None,
    callback_url: str | None = None,
    slug: str | None = None,
):
    """
    Endpoint genérico para criar link curto e QR sem vínculo com sessão.
    Parâmetros via querystring:
      - long_url (obrigatório)
      - name (opcional)
      - callback_url (opcional)
      - slug (opcional)
    """
    try:
        data, short_url = await create_short_link(
            long_url,
            session_id=None,
            name=name,
            callback_url=callback_url,
            slug=slug,
        )
        return {
            "ok": True,
            "slug": data.slug,
            "short_url": short_url,
            "qr_png": str(data.qr_png),
            "qr_svg": str(data.qr_svg),
        }
    except Exception as e:
        raise HTTPException(502, str(e))


@router.post("/session/check")
async def session_check(body: CheckWithSession):
    svc = CRMService()
    try:
        res = svc.check_and_next_step(body.cpf)
        s = await set_crm_result(
            body.sessionId,
            isRegistered=res["isRegistered"],
            isComplete=res["isComplete"],
            nextStep=res["nextStep"],
            cpf=body.cpf,  # guarda cpf na sessão
        )
        return {"ok": True, "session": s}
    except Exception as e:
        raise HTTPException(502, str(e))

class RegisterWithSession(UpsertRequest):
    sessionId: str

@router.post("/session/register")
async def session_register(body: RegisterWithSession):
    svc = CRMService()
    try:
        out = svc.upsert(
            cpf=body.cpf,
            email=body.email,
            mobileNumber=body.mobileNumber,
            birthday=body.birthday,
            fullName=body.fullName,
            address=body.address.model_dump(),
        )
        s = await advance(body.sessionId, "continue")
        return {"ok": True, "client": out, "session": s}
    except Exception as e:
        raise HTTPException(502, str(e))


@router.post("/session/continue")
async def session_continue(body: ContinueRequest):
    async with serial_lock:
        udp_sender.send("INSTRUCOES")
    return await advance(body.sessionId, "instructions")


@router.post("/authorize")
async def authorize(body: ContinueRequest):
    s = await mark_authorized(body.sessionId)
    return {"ok": True, "session": s}


@router.post("/session/advance")
async def session_advance(body: NextRequest):
    step = body.step
    async with serial_lock:
        if step == "capture":
            udp_sender.send("CAPTURA")
        elif step == "approve":
            udp_sender.send("VALIDACAO")
        elif step == "instructions":
            udp_sender.send("INSTRUCOES")
    return await advance(body.sessionId, step)
