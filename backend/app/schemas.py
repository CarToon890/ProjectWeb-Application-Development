from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

FurnitureType = Literal["sofa", "table", "chair", "bed", "wardrobe", "shelf", "other"]
Condition = Literal["good", "fair", "poor"]
Role = Literal["user", "admin", "staff"]
ItemStatus = Literal["pending", "assessed", "scheduled", "picked_up", "donated"]
BookingStatus = Literal["pending", "confirmed", "in_transit", "completed", "cancelled"]


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UsernameAvailable(BaseModel):
    available: bool


# ---------- User ----------
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Role
    created_at: datetime


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


# แยกออกจาก UserUpdate โดยตั้งใจ — ผูก endpoint คนละตัวที่ยอมให้ admin เท่านั้นเรียก
# กัน user ทั่วไปยิง PUT /users/{id} พร้อม field "role" มาแล้วเลื่อนสิทธิ์ตัวเอง
class UserRoleUpdate(BaseModel):
    role: Role


# ---------- Item ----------
class ItemCreate(BaseModel):
    furniture_type: FurnitureType
    condition: Condition
    description: Optional[str] = None
    photo_url: Optional[str] = None


class ItemUpdate(BaseModel):
    furniture_type: Optional[FurnitureType] = None
    condition: Optional[Condition] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None


class ItemRead(BaseModel):
    id: int
    user_id: int
    furniture_type: str
    condition: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    estimated_price: int
    co2_saved_kg: float
    status: str
    created_at: datetime


# ---------- Product ----------
class ProductCreate(BaseModel):
    name: str
    category: str
    price: int
    image_url: Optional[str] = None
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None


class ProductRead(BaseModel):
    id: int
    name: str
    category: str
    price: int
    image_url: Optional[str] = None
    stock: int


# ---------- Timeslot ----------
class TimeslotCreate(BaseModel):
    datetime: datetime
    technician_name: str


class TimeslotUpdate(BaseModel):
    datetime: Optional[datetime] = None
    technician_name: Optional[str] = None
    is_available: Optional[bool] = None


class TimeslotRead(BaseModel):
    id: int
    datetime: datetime
    technician_name: str
    is_available: bool


# ---------- Booking ----------
class BookingCreate(BaseModel):
    item_id: int
    product_id: Optional[int] = None
    timeslot_id: int
    address: str


class BookingRead(BaseModel):
    id: int
    user_id: int
    item_id: int
    product_id: Optional[int] = None
    timeslot_id: int
    address: str
    total_price: int
    status: str
    created_at: datetime


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


# รวม booking + item/product/timeslot/user ไว้ก้อนเดียว กันหน้า booking-detail/checklist ต้องยิงหลาย request
class BookingDetailRead(BaseModel):
    id: int
    address: str
    total_price: int
    status: str
    created_at: datetime
    item: ItemRead
    product: Optional[ProductRead] = None
    timeslot: TimeslotRead
    user: UserRead


# ---------- Upload ----------
class UploadResponse(BaseModel):
    url: str


# ---------- Eco ----------
class EcoStats(BaseModel):
    total_items: int
    total_co2_saved_kg: float
    by_category: dict[str, int]
