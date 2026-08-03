from datetime import datetime
from typing import Optional

from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    furniture_type: str
    condition: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    estimated_price: int
    co2_saved_kg: float
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    price: int
    image_url: Optional[str] = None
    stock: int


class Timeslot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    datetime: datetime
    technician_name: str
    is_available: bool = Field(default=True)


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    item_id: int = Field(foreign_key="item.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    timeslot_id: int = Field(foreign_key="timeslot.id")
    address: str
    total_price: int
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # unique เฉพาะการจองที่ยัง active — จอง timeslot เดิมซ้ำได้หลัง cancel
    __table_args__ = (
        Index(
            "ix_booking_timeslot_active_unique",
            "timeslot_id",
            unique=True,
            postgresql_where=text("status != 'cancelled'"),
            sqlite_where=text("status != 'cancelled'"),
        ),
    )
