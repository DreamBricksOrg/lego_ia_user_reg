from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.totem_service import create_session, get_session, set_crm_result, mark_authorized, advance
from services.crm_service import CRMService
from schemas.crm import CheckRequest, UpsertRequest

router = APIRouter(prefix="/totem", tags=["totem"])

class StartResponse(BaseModel):
    sessionId: str
    step: str

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

class TermsRequest(BaseModel):
    sessionId: str
    accepted: bool

@router.post("/session/terms")
async def accept_terms(body: TermsRequest):
    if not body.accepted:
        raise HTTPException(400, "terms not accepted")
    return await advance(body.sessionId, "check")

class CheckWithSession(CheckRequest):
    sessionId: str

@router.post("/session/check")
async def session_check(body: CheckWithSession):
    svc = CRMService()
    try:
        res = svc.check_and_next_step(body.cpf)
        s = await set_crm_result(body.sessionId, **res)
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

class ContinueRequest(BaseModel):
    sessionId: str

@router.post("/session/continue")
async def session_continue(body: ContinueRequest):
    return await advance(body.sessionId, "instructions")

@router.post("/authorize")
async def authorize(body: ContinueRequest):
    s = await mark_authorized(body.sessionId)
    return {"ok": True, "session": s}

class NextRequest(BaseModel):
    sessionId: str
    step: str

@router.post("/session/advance")
async def session_advance(body: NextRequest):
    return await advance(body.sessionId, body.step)
