from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.schemas import LoanRead, MemberCreate, MemberRead, MemberUpdate
from src.services import loan_service, member_service
from src.utils.database import get_db

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=list[MemberRead])
def list_members(
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return member_service.list_members(db, search, skip, limit)


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    return member_service.create_member(db, data)


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_service.get_member(db, member_id)


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(member_id: int, data: MemberUpdate, db: Session = Depends(get_db)):
    return member_service.update_member(db, member_id, data)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member_service.delete_member(db, member_id)


@router.get("/{member_id}/loans", response_model=list[LoanRead])
def member_loans(
    member_id: int, active_only: bool = False, db: Session = Depends(get_db)
):
    member_service.get_member(db, member_id)  # 404 if missing
    return loan_service.list_loans(db, member_id=member_id, active_only=active_only)
