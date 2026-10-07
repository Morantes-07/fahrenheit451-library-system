from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str = Field(min_length=10, max_length=20)
    published_year: int | None = Field(default=None, ge=0, le=2100)


class BookCreate(BookBase):
    copies_total: int = Field(default=1, ge=1)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, min_length=10, max_length=20)
    published_year: int | None = Field(default=None, ge=0, le=2100)
    copies_total: int | None = Field(default=None, ge=1)


class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    copies_total: int
    copies_available: int
    created_at: datetime
