from datetime import datetime, timezone
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    furniture_type: str
    condition: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    estimated_price: int
    co2_saved_kg: float
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str = Field(index=True)
    price: int
    image_url: Optional[str] = None
    stock: int


class Timeslot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    datetime: datetime
    technician_name: str
    is_available: bool = Field(default=True)

    # Composite Index: กรอง is_available + datetime และช่วย ORDER BY datetime โดยไม่ต้อง Sort
    __table_args__ = (
        Index("ix_timeslot_available_datetime", "is_available", "datetime"),
    )


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    timeslot_id: int = Field(foreign_key="timeslot.id", index=True)
    address: str
    total_price: int
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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


class MarketListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="user.id", index=True)
    title: str
    furniture_type: str
    condition: str
    description: str
    price: int
    image_url: Optional[str] = None
    status: str = Field(default="available", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketChat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="marketlisting.id", index=True)
    buyer_id: int = Field(foreign_key="user.id", index=True)
    seller_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="marketchat.id", index=True)
    sender_id: int = Field(foreign_key="user.id", index=True)
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="marketlisting.id", index=True)
    buyer_id: int = Field(foreign_key="user.id", index=True)
    seller_id: int = Field(foreign_key="user.id", index=True)
    item_price: int
    shipping_fee: int
    address: str
    status: str = Field(default="awaiting_payment", index=True)
    payment_proof_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    refund_reason: Optional[str] = None
    refund_proof_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

