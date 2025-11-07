from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from pydantic_extra_types.phone_numbers import PhoneNumber


class Registration(BaseModel):
    email: EmailStr
    birthday: date = Field(..., description="Data de nascimento (YYYY-MM-DD)")
    