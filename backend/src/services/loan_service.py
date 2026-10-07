import math
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Loan
from src.schemas import LoanCreate
from src.services.book_service import get_book
from src.services.member_service import get_member
from src.utils.config import settings
from src.utils.exceptions import BusinessRuleError, NotFoundError
from src.utils.helpers import utcnow


def get_loan(db: Session, loan_id: int) -> Loan:
    loan = db.get(Loan, loan_id)
    if not loan:
        raise NotFoundError(f"Loan {loan_id} not found")
    return loan


def list_loans(
    db: Session,
    member_id: int | None = None,
    book_id: int | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Loan]:
    stmt = select(Loan)
    if member_id is not None:
        stmt = stmt.where(Loan.member_id == member_id)
    if book_id is not None:
        stmt = stmt.where(Loan.book_id == book_id)
    if active_only:
        stmt = stmt.where(Loan.returned_at.is_(None))
    stmt = stmt.order_by(Loan.borrowed_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def list_overdue_loans(db: Session) -> list[Loan]:
    stmt = (
        select(Loan)
        .where(Loan.returned_at.is_(None), Loan.due_date < utcnow())
        .order_by(Loan.due_date)
    )
    return list(db.scalars(stmt))


def borrow_book(db: Session, data: LoanCreate) -> Loan:
    member = get_member(db, data.member_id)
    book = get_book(db, data.book_id)

    if not member.is_active:
        raise BusinessRuleError("Member account is inactive")
    if book.copies_available < 1:
        raise BusinessRuleError("No copies of this book are available")

    active_count = db.scalar(
        select(func.count(Loan.id)).where(
            Loan.member_id == member.id, Loan.returned_at.is_(None)
        )
    )
    if active_count >= settings.MAX_ACTIVE_LOANS:
        raise BusinessRuleError(
            f"Member reached the limit of {settings.MAX_ACTIVE_LOANS} active loans"
        )

    already = db.scalar(
        select(Loan.id).where(
            Loan.member_id == member.id,
            Loan.book_id == book.id,
            Loan.returned_at.is_(None),
        )
    )
    if already:
        raise BusinessRuleError("Member already has this book on loan")

    # Member must not hold overdue books
    overdue = db.scalar(
        select(Loan.id).where(
            Loan.member_id == member.id,
            Loan.returned_at.is_(None),
            Loan.due_date < utcnow(),
        )
    )
    if overdue:
        raise BusinessRuleError("Member has overdue books; return them first")

    now = utcnow()
    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        borrowed_at=now,
        due_date=now + timedelta(days=settings.LOAN_DAYS),
    )
    book.copies_available -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_book(db: Session, loan_id: int) -> Loan:
    loan = get_loan(db, loan_id)
    if loan.returned_at is not None:
        raise BusinessRuleError("This loan was already returned")

    now = utcnow()
    loan.returned_at = now
    if now > loan.due_date:
        days_late = math.ceil((now - loan.due_date).total_seconds() / 86400)
        loan.fine_amount = round(days_late * settings.FINE_PER_DAY, 2)

    loan.book.copies_available += 1
    db.commit()
    db.refresh(loan)
    return loan


def renew_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan(db, loan_id)
    if loan.returned_at is not None:
        raise BusinessRuleError("Cannot renew a loan that was already returned")
    if loan.is_overdue:
        raise BusinessRuleError("Cannot renew an overdue loan")

    loan.due_date = loan.due_date + timedelta(days=settings.LOAN_DAYS)
    db.commit()
    db.refresh(loan)
    return loan
