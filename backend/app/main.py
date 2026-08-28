import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
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


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "The Disposal Guilt API"}


# Mount static frontend for local dev if directory exists
frontend_path = "frontend"
if not os.path.exists(frontend_path):
    # Try finding frontend relative to this file
    alt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
    if os.path.exists(alt_path):
        frontend_path = alt_path

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
