from src.routes.books import router as books_router
from src.routes.members import router as members_router
from src.routes.loans import router as loans_router

__all__ = ["books_router", "members_router", "loans_router"]