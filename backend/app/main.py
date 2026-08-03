from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers import auth, bookings, eco, items, products, users
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_data(session)
    yield


app = FastAPI(title="The Disposal Guilt API", lifespan=lifespan)

# dev-only: อนุญาตทุก origin เพื่อให้ frontend ที่เปิดจากที่ไหนก็เรียก API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(items.router, prefix="/api", tags=["items"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(bookings.router, prefix="/api", tags=["bookings"])
app.include_router(eco.router, prefix="/api", tags=["eco"])

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
