from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.schemas import LoanCreate, LoanRead
from src.services import loan_service
from src.utils.database import get_db

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get("", response_model=list[LoanRead])
def list_loans(
    member_id: int | None = None,
    book_id: int | None = None,
    active_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return loan_service.list_loans(db, member_id, book_id, active_only, skip, limit)


# Declared before "/{loan_id}" so "overdue" is not parsed as an id
@router.get("/overdue", response_model=list[LoanRead])
def overdue_loans(db: Session = Depends(get_db)):
    return loan_service.list_overdue_loans(db)


@router.post("/borrow", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def borrow_book(data: LoanCreate, db: Session = Depends(get_db)):
    return loan_service.borrow_book(db, data)


@router.get("/{loan_id}", response_model=LoanRead)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.get_loan(db, loan_id)


@router.post("/{loan_id}/return", response_model=LoanRead)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.return_book(db, loan_id)


@router.post("/{loan_id}/renew", response_model=LoanRead)
def renew_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.renew_loan(db, loan_id)
