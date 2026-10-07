from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class MemberBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    phone: str | None = Field(default=None, max_length=30)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None


class MemberRead(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    joined_at: datetime
