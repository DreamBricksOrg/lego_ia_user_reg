import structlog
from typing import Any, Dict, Optional
import httpx

from src.core.config import settings

logger = structlog.get_logger()


class CRMError(Exception):
  pass


class CRMClient:
  def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, mall_id: Optional[int] = None):
    self.base_url = (base_url or settings.CRM_BASE_URL).rstrip("/")
    self.api_key = api_key or settings.CRM_API_KEY
    self.mall_id = mall_id or settings.CRM_MALL_ID
    self._headers = {"x-partner-key": self.api_key}
    self._timeout = httpx.Timeout(15.0)


  def _params(self) -> Dict[str, Any]:
    return {"mallId": str(self.mall_id)}


  def _client(self) -> httpx.Client:
    return httpx.Client(base_url=self.base_url, headers=self._headers, timeout=self._timeout)


  def check_client(self, cpf: str) -> Dict[str, bool]:
    url = f"/clients/{cpf}/is-registered"
    with self._client() as c:
      r = c.get(url, params=self._params())
    if r.status_code >= 400:
      raise CRMError(f"check_client failed: {r.status_code} {r.text}")
    data = r.json()
    is_registered = str(data.get("isRegistered", "false")).lower() == "true"
    is_complete = str(data.get("isComplete", "false")).lower() == "true"
    return {"isRegistered": is_registered, "isComplete": is_complete}


  def upsert_client(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    with self._client() as c:
      r = c.post("/clients", params=self._params(), json=payload)
    if r.status_code >= 400:
      raise CRMError(f"upsert_client failed: {r.status_code} {r.text}")
    return r.json()


  def track_interaction(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
    body = {"trackData": track_data}
    with self._client() as c:
      r = c.post("/track/interaction", params=self._params(), json=body)
    if r.status_code >= 400:
      raise CRMError(f"track_interaction failed: {r.status_code} {r.text}")
    return r.json()