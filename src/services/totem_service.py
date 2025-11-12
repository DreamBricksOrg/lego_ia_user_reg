from __future__ import annotations
import uuid
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.redis_client import get_redis
from core.config import settings
from utils.shortener_client import create_short_link


SESSION_TTL_SECONDS = 60 * 30  # 30 minutes


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _key(session_id: str) -> str:
    return f"totem:session:{session_id}"


async def create_session() -> Dict[str, Any]:
    session_id = uuid.uuid4().hex
    data = {
        "sessionId": session_id,
        "createdAt": _now_iso(),
        "updatedAt": _now_iso(),
        "step": "terms",
        "flags": {},
        "crm": {},
        "qr": {},
        "meta": {},
    }
    r = get_redis()
    await r.set(_key(session_id), json.dumps(data), ex=SESSION_TTL_SECONDS)
    return data


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    r = get_redis()
    raw = await r.get(_key(session_id))
    if not raw:
        return None
    return json.loads(raw)


async def save_session(session: Dict[str, Any]) -> None:
    session["updatedAt"] = _now_iso()
    r = get_redis()
    await r.set(_key(session["sessionId"]), json.dumps(session), ex=SESSION_TTL_SECONDS)


async def set_step(session_id: str, step: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    s = await get_session(session_id)
    if s is None:
        raise KeyError("invalid session")
    s["step"] = step
    if extra:
        s.update(extra)
    await save_session(s)
    return s


async def set_crm_result(
    session_id: str,
    *,
    isRegistered: bool,
    isComplete: bool,
    nextStep: str,
    cpf: str | None = None,
    **_extras,   # ignora quaisquer chaves adicionais
) -> Dict[str, Any]:
    s = await get_session(session_id)
    if s is None:
        raise KeyError("invalid session")
    s.setdefault("crm", {})
    s["crm"].update({
        "isRegistered": isRegistered,
        "isComplete": isComplete,
        "nextStep": nextStep,
    })
    if cpf:
        s["crm"]["cpf"] = cpf

    s["step"] = "data" if nextStep == "register" else "continue"
    await save_session(s)
    return s


async def mark_authorized(session_id: str) -> Dict[str, Any]:
    s = await set_step(session_id, "instructions")
    s["flags"]["authorized"] = True
    await save_session(s)
    return s


async def advance(session_id: str, to_step: str) -> Dict[str, Any]:
    return await set_step(session_id, to_step)


async def init_qr_for_session(session_id: str) -> Dict[str, Any]:
    """
    Gera short link + QR (PNG/SVG) no encurtador e salva na sessão.
    Long URL: CADASTRO_BASE_URL?sid=<session_id>
    """
    long_url = f"{settings.CADASTRO_BASE_URL.rstrip('/')}/api/lego/termos?sid={session_id}"
    shortener_data, short_url = await create_short_link(long_url, session_id=session_id, name=f"LEGO sid {session_id}")
    s = await get_session(session_id)
    if s is None:
        raise KeyError("invalid session")
    s.setdefault("qr", {})
    s["qr"].update({
        "slug": shortener_data.slug,
        "short_url": short_url,
        "qr_png": str(shortener_data.qr_png),
        "qr_svg": str(shortener_data.qr_svg),
    })
    await save_session(s)
    return s

async def close_session(session_id: str) -> Dict[str, Any]:
    """Encerra a sessão e impede novas ações."""
    s = await get_session(session_id)
    if not s:
        raise KeyError("invalid session")
    s["step"] = "closed"
    s.setdefault("flags", {})["ended"] = True
    s["endedAt"] = _now_iso()

    # Atualiza no Redis e expira mais rápido
    r = get_redis()
    await r.set(_key(session_id), json.dumps(s), ex=60)
    return s
