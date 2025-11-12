from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

import httpx
from core.config import settings


class LogCenterSender:
    """
    Envia logs para POST {base}/logs/.
    - follow_redirects=True
    - Retorno detalhado p/ depurar (status e corpo)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.base_url = (base_url or settings.LOGCENTER_BASE_URL or "").rstrip("/")
        self.project_id = project_id or settings.LOGCENTER_PROJECT_ID
        self.api_key = api_key or settings.LOGCENTER_API_KEY
        self.timeout = httpx.Timeout(timeout, connect=timeout)

    def _headers(self) -> Dict[str, str]:
        h = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            h["x_api_key"] = self.api_key
        return h

    async def send_log_detailed(
        self,
        level: str,
        message: str,
        *,
        tags: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not (self.base_url and self.project_id and self.api_key):
            return {"ok": False, "error": "missing_config"}

        level = (level or "INFO").upper()
        now_iso = datetime.now(timezone.utc).isoformat()
        if status is None:
            status = "ERROR" if level in ("ERROR", "CRITICAL", "FATAL") else "OK"

        payload: Dict[str, Any] = {
            "project_id": self.project_id,
            "level": level,
            "message": message,
            "timestamp": now_iso,
            "status": status,
        }
        if tags:
            payload["tags"] = tags
        if data:
            payload["data"] = data
        if request_id:
            payload["request_id"] = request_id

        url = f"{self.base_url}/logs/"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)
        except Exception as e:
            return {"ok": False, "exception": str(e), "url": url}

        try:
            body = resp.json()
        except Exception:
            body = {"text": resp.text}

        return {
            "ok": 200 <= resp.status_code < 300,
            "status": resp.status_code,
            "response": body,
            "url": url,
        }

    async def send_log(
        self,
        level: str,
        message: str,
        *,
        tags: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        res = await self.send_log_detailed(
            level, message, tags=tags, data=data, request_id=request_id, status=status
        )
        return bool(res.get("ok"))

    def send_log_sync(
        self,
        level: str,
        message: str,
        *,
        tags: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            loop.create_task(self.send_log(level, message, tags=tags, data=data, request_id=request_id, status=status))
            return True
        else:
            return asyncio.run(self.send_log(level, message, tags=tags, data=data, request_id=request_id, status=status))
