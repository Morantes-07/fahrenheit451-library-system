from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models import Book, Loan
from src.schemas import BookCreate, BookUpdate
from src.utils.exceptions import BusinessRuleError, ConflictError, NotFoundError


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise NotFoundError(f"Book {book_id} not found")
    return book


def list_books(
    db: Session,
    search: str | None = None,
    available_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Book]:
    stmt = select(Book)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )
    if available_only:
        stmt = stmt.where(Book.copies_available > 0)
    stmt = stmt.order_by(Book.title).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def _isbn_taken(db: Session, isbn: str, exclude_id: int | None = None) -> bool:
    stmt = select(Book.id).where(Book.isbn == isbn)
    if exclude_id is not None:
        stmt = stmt.where(Book.id != exclude_id)
    return db.scalar(stmt) is not None


def create_book(db: Session, data: BookCreate) -> Book:
    if _isbn_taken(db, data.isbn):
        raise ConflictError(f"A book with ISBN {data.isbn} already exists")
    book = Book(**data.model_dump(), copies_available=data.copies_total)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    changes = data.model_dump(exclude_unset=True)

    if "isbn" in changes and _isbn_taken(db, changes["isbn"], exclude_id=book.id):
        raise ConflictError(f"A book with ISBN {changes['isbn']} already exists")

    if "copies_total" in changes and changes["copies_total"] is not None:
        on_loan = book.copies_total - book.copies_available
        if changes["copies_total"] < on_loan:
            raise BusinessRuleError(
                f"Cannot set copies below the {on_loan} currently on loan"
            )
        book.copies_available = changes["copies_total"] - on_loan

    for field, value in changes.items():
        if value is not None:
            setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    has_loans = db.scalar(select(Loan.id).where(Loan.book_id == book.id).limit(1))
    if has_loans:
        raise ConflictError("Cannot delete a book that has loan history")
    db.delete(book)
    db.commit()
