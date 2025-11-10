from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field
from pydantic_br import CPF



class CheckRequest(BaseModel):
  cpf: CPF = Field(..., description="CPF do cliente (somente números)")


class CheckResponse(BaseModel):
  isRegistered: bool
  isComplete: bool
  nextStep: Literal["pass", "register"]


class Address(BaseModel):
  zipCode: str
  street: str
  number: str
  complement: Optional[str] = None
  neighborhood: str
  city: str
  state: str


class UpsertRequest(BaseModel):
  cpf: CPF
  email: EmailStr
  mobileNumber: str
  birthday: date
  fullName: Optional[str] = None
  address: Address


class UpsertResponse(BaseModel):
  ok: bool
  clientId: Optional[str] = None
  raw: Optional[dict] = None


class InteractionTrack(BaseModel):
  name: str
  description: Optional[str] = None
  type: Optional[str] = None
  startDate: Optional[datetime] = None
  endDate: Optional[datetime] = None


class InteractionRequest(BaseModel):
  cpf: Optional[CPF] = None
  email: Optional[EmailStr] = None
  phone: Optional[str] = None
  track: InteractionTrack
  metadata: Optional[dict] = None
  customFields: Optional[dict] = None


class InteractionResponse(BaseModel):
  ok: bool
  raw: Optional[dict] = None


class TotemAuthorizeRequest(BaseModel):
  sessionId: str


class TotemAuthorizeResponse(BaseModel):
  sessionId: str