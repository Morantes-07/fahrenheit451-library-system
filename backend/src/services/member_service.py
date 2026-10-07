from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models import Loan, Member
from src.schemas import MemberCreate, MemberUpdate
from src.utils.exceptions import BusinessRuleError, ConflictError, NotFoundError


def get_member(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if not member:
        raise NotFoundError(f"Member {member_id} not found")
    return member


def list_members(
    db: Session, search: str | None = None, skip: int = 0, limit: int = 50
) -> list[Member]:
    stmt = select(Member)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Member.full_name.ilike(like), Member.email.ilike(like)))
    stmt = stmt.order_by(Member.full_name).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def _email_taken(db: Session, email: str, exclude_id: int | None = None) -> bool:
    stmt = select(Member.id).where(Member.email == email)
    if exclude_id is not None:
        stmt = stmt.where(Member.id != exclude_id)
    return db.scalar(stmt) is not None


def create_member(db: Session, data: MemberCreate) -> Member:
    if _email_taken(db, data.email):
        raise ConflictError(f"A member with email {data.email} already exists")
    member = Member(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member_id: int, data: MemberUpdate) -> Member:
    member = get_member(db, member_id)
    changes = data.model_dump(exclude_unset=True)

    if "email" in changes and _email_taken(db, changes["email"], exclude_id=member.id):
        raise ConflictError(f"A member with email {changes['email']} already exists")

    for field, value in changes.items():
        if value is not None:
            setattr(member, field, value)

    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> None:
    member = get_member(db, member_id)
    active = db.scalar(
        select(Loan.id)
        .where(Loan.member_id == member.id, Loan.returned_at.is_(None))
        .limit(1)
    )
    if active:
        raise BusinessRuleError("Member still has books to return")
    has_history = db.scalar(select(Loan.id).where(Loan.member_id == member.id).limit(1))
    if has_history:
        raise ConflictError(
            "Member has loan history; deactivate the member instead of deleting"
        )
    db.delete(member)
    db.commit()
