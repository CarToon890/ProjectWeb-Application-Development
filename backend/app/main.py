import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers import auth, bookings, eco, items, products, staff, uploads, users
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_db_and_tables()
        with Session(engine) as session:
            seed_data(session)
    except Exception as e:
        print(f"[Lifespan Notice] Database init warning: {e}")
    yield


app = FastAPI(title="The Disposal Guilt API", lifespan=lifespan)


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    # Keep diagnostics useful without logging request bodies, credentials, or
    # database exception text that may contain user-provided values.
    print(
        f"Unhandled API exception path={request.url.path} exception={type(exc).__name__}",
        flush=True,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(items.router, prefix="/api", tags=["items"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(bookings.router, prefix="/api", tags=["bookings"])
app.include_router(eco.router, prefix="/api", tags=["eco"])
app.include_router(uploads.router, prefix="/api", tags=["uploads"])
app.include_router(staff.router, prefix="/api", tags=["staff"])


from app.database import ENGINE_ERROR, RAW_DATABASE_URL
from app.models import User
from sqlmodel import select


@app.get("/api/health", tags=["health"])
def health_check():
    db_url_str = str(engine.url)
    if "@" in db_url_str:
        prefix, suffix = db_url_str.split("@", 1)
        driver = prefix.split(":")[0]
        safe_url = f"{driver}://***@{suffix}"
    else:
        safe_url = db_url_str

    raw_env = os.environ.get("DATABASE_URL")
    has_raw_env = bool(raw_env)
    env_masked = None
    if raw_env:
        if "@" in raw_env:
            p, s = raw_env.split("@", 1)
            env_masked = f"{p.split(':')[0]}://***@{s}"
        else:
            env_masked = raw_env[:15] + "..."

    db_connected = False
    user_count = -1
    query_err = None
    try:
        with Session(engine) as s:
            users = s.exec(select(User)).all()
            user_count = len(users)
            db_connected = True
    except Exception as e:
        query_err = str(e)

    return {
        "status": "ok",
        "service": "The Disposal Guilt API",
        "has_database_url_env": has_raw_env,
        "env_database_url_target": env_masked,
        "active_engine_url": safe_url,
        "engine_creation_error": ENGINE_ERROR,
        "db_connected": db_connected,
        "user_count": user_count,
        "query_error": query_err,
    }




# Mount static frontend for local dev if directory exists
frontend_path = "frontend"
if not os.path.exists(frontend_path):
    # Try finding frontend relative to this file
    alt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
    if os.path.exists(alt_path):
        frontend_path = alt_path

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
