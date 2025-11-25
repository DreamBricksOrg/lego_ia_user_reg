import structlog
from datetime import date, datetime
from typing import Any, Dict, Optional

from integration.crm_client import CRMClient
from core.config import settings


logger = structlog.get_logger()


class CRMService:
  def __init__(self, client: Optional[CRMClient] = None):
    self.client = client or CRMClient()


  def check_and_next_step(self, cpf: str) -> Dict[str, Any]:
    if not getattr(settings, "CRM_API_KEY", None):
      return {
          "cpf": cpf,
          "isRegistered": True,
          "isComplete": True,
          "mocked": True,
          "nextStep": "pass"
      }
    res = self.client.check_client(cpf)
    next_step = "pass" if (res["isRegistered"] and res["isComplete"]) else "register"
    return {**res, "nextStep": next_step}


  def upsert(
      self,
      *,
      cpf: str,
      email: str,
      mobileNumber: str,
      birthday: date,
      fullName: Optional[str],
      address: Dict[str, Any],
  ) -> Dict[str, Any]:
      address_str: Dict[str, str] = {
        str(key): "" if value is None else str(value)
        for key, value in address.items()
      }

      payload = {
          "cpf": cpf,
          "email": email,
          "mobileNumber": mobileNumber,
          "birthday": birthday.isoformat(),
          "address": address_str,
          "originRegistryId": settings.CRM_ORIGIN_ID,
      }
      if fullName:
          payload["fullName"] = fullName

      logger.info(
          "crm_upsert_request",
          extra={"cpf_mask": cpf[-4:], "has_name": bool(fullName)},
      )
      return self.client.upsert_client(payload)

  def interaction(self, *, email: Optional[str], phone: Optional[str], track: Dict[str, Any], metadata: Optional[dict], customFields: Optional[dict]) -> Dict[str, Any]:
    track_data: Dict[str, Any] = {
      "track": {
      "trackType": track.get("type") or settings.CRM_TRACK_TYPE,
      "name": track.get("name") or settings.CRM_TRACK_NAME,
      "description": track.get("description"),
      "startDate": track.get("startDate") or datetime.now().isoformat(),
      "endDate": track.get("endDate") or datetime.now().isoformat(),
    },
      "customer": {},
    }
    
    if email:
      track_data["customer"]["email"] = email
    if phone:
      track_data["customer"]["mobileNumber"] = phone

    if metadata:
      track_data["metadata"] = metadata
    if customFields:
      track_data["customFields"] = customFields

    return self.client.track_interaction(track_data)
