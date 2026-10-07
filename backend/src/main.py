from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routes import books_router, loans_router, members_router
from src.utils.config import settings
from src.utils.database import init_db
from src.utils.exceptions import (
    BusinessRuleError,
    ConflictError,
    LibraryError,
    NotFoundError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # creates the tables if they don't exist
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)
app.include_router(members_router)
app.include_router(loans_router)


_STATUS = {NotFoundError: 404, ConflictError: 409, BusinessRuleError: 400}


@app.exception_handler(LibraryError)
async def library_error_handler(_: Request, exc: LibraryError):
    code = next((c for t, c in _STATUS.items() if isinstance(exc, t)), 400)
    return JSONResponse(status_code=code, content={"detail": exc.message})


@app.get("/", tags=["Health"])
def health():
    return {"app": settings.APP_NAME, "status": "ok"}
