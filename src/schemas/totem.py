from pydantic import BaseModel
from schemas.crm import CheckRequest


class StartResponse(BaseModel):
    sessionId: str
    step: str


class TermsRequest(BaseModel):
    sessionId: str
    accepted: bool


class QRInitRequest(BaseModel):
    sessionId: str | None = None


class QRInitResponse(BaseModel):
    sessionId: str
    short_url: str | None = None
    qr_png: str | None = None
    qr_svg: str | None = None


class CheckWithSession(CheckRequest):
    sessionId: str


class ContinueRequest(BaseModel):
    sessionId: str


class NextRequest(BaseModel):
    sessionId: str
    step: str  # "capture" | "approve" | "result" etc.
