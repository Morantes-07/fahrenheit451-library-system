from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.database import Base
from src.utils.helpers import utcnow


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0)

    book: Mapped["Book"] = relationship(back_populates="loans")  # noqa: F821
    member: Mapped["Member"] = relationship(back_populates="loans")  # noqa: F821

    @property
    def is_overdue(self) -> bool:
        return self.returned_at is None and utcnow() > self.due_date
