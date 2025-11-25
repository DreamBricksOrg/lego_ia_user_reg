import structlog
from fastapi import APIRouter, Depends, HTTPException

from schemas.crm import (
  CheckRequest,
  CheckResponse,
  UpsertRequest,
  UpsertResponse,
  InteractionRequest,
  InteractionResponse,
)
from services.crm_service import CRMService


logger = structlog.get_logger()
router = APIRouter(prefix="/crm", tags=["crm"])


def get_service() -> CRMService:
  return CRMService()


@router.post("/check", response_model=CheckResponse)
def crm_check(body: CheckRequest, svc: CRMService = Depends(get_service)):
  try:
    return CheckResponse(**svc.check_and_next_step(cpf=body.cpf))
  except Exception as e:
    logger.exception("crm_check_error")
    raise HTTPException(status_code=502, detail=str(e))


@router.post("/upsert", response_model=UpsertResponse)
def crm_upsert(body: UpsertRequest, svc: CRMService = Depends(get_service)):
  try:
    out = svc.upsert(
      cpf=body.cpf,
      email=body.email,
      mobileNumber=body.mobileNumber,
      birthday=body.birthday,
      fullName=body.fullName,
      address=body.address.model_dump(),
    )
    client_id = out.get("id") or out.get("clientId")
    return UpsertResponse(ok=True, clientId=str(client_id) if client_id else None, raw=out)
  except Exception as e:
    logger.exception("crm_upsert_error")
    raise HTTPException(status_code=502, detail=str(e))



@router.post("/interaction", response_model=InteractionResponse)
def crm_interaction(body: InteractionRequest, svc: CRMService = Depends(get_service)):
  try:
    out = svc.interaction(
      email=body.email,
      phone=body.phone,
      track=body.track.model_dump(),
      metadata=body.metadata,
      customFields=body.customFields,
    )
    return InteractionResponse(ok=True, raw=out)
  except Exception as e:
    logger.exception("crm_interaction_error")
    raise HTTPException(status_code=502, detail=str(e))
  