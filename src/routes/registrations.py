import uuid
import structlog

from datetime import datetime, date, timedelta, timezone, time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument, ReadPreference

from schemas.user import (
    UserInitRequest,
    UserInitResponse,
    UserUpdateRequest,
    UserGetResponse,
    UserPickupRequest,
    UserPickupResponse,
)

log = structlog.get_logger()
router = APIRouter(prefix="/api/users")

def today_utc_date() -> date:
    return datetime.now(timezone.utc)

@router.post("/", response_model=UserInitResponse)
async def create_user(payload: UserInitRequest):
    reg_id = str(uuid.uuid4())
    today = today_utc_date()
    register_day = payload.registerDay or today

    doc = {
        "_id": reg_id,
        "code": payload.code,
        "name": payload.name,
        "email": str(payload.email).lower(),
        "registerDay": register_day,             # date
        "canPickFrom": register_day,             # date
        "status": "registered",                  # registered
        "createdAt": today,                      # date
        "updatedAt": today,                      # date
        "pickedDay": None,                       # date|None
        "condomsPicked": 0,                       # int
        "createdAt": today,                      # date
        "updatedAt": today,                      # date
    }

    # try:
    #     await 
    # except DuplicateKeyError:
    #     log.warning("email-already-exists", email=payload.email, collection=collection)
    #     raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    log.info("user-created", id=reg_id)

    return UserInitResponse(
        id=reg_id,
        name=doc["name"],
        email=doc["email"],
        status=doc["status"],
        registerDay=doc["registerDay"],
        canPickFrom=doc["canPickFrom"],
    )

