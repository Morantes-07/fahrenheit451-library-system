from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.schemas import BookCreate, BookRead, BookUpdate
from src.services import book_service
from src.utils.database import get_db

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookRead])
def list_books(
    search: str | None = None,
    available_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return book_service.list_books(db, search, available_only, skip, limit)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, data)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.get_book(db, book_id)


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    return book_service.update_book(db, book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_service.delete_book(db, book_id)
