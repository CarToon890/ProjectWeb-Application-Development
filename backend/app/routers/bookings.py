from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.auth import get_current_admin, get_current_staff, get_current_user
from app.database import get_session
from app.models import Booking, Item, Product, Timeslot, User
from app.schemas import (
    BookingCreate,
    BookingDetailRead,
    BookingRead,
    BookingStatusUpdate,
    ItemRead,
    ProductRead,
    TimeslotCreate,
    TimeslotRead,
    TimeslotUpdate,
    UserRead,
)

router = APIRouter()

# booking status ที่เข้ามาแล้ว item ควรอัปเดตสถานะตามไปด้วย
ITEM_STATUS_ON_BOOKING_STATUS = {
    "in_transit": "picked_up",
    "completed": "donated",
}


def _require_owner_or_admin(booking: Booking, current: User) -> None:
    if current.role != "admin" and booking.user_id != current.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์เข้าถึงการจองนี้")


def _require_access(booking: Booking, current: User) -> None:
    # staff ต้องดูรายละเอียดงานที่ตัวเองไปรับ-ส่งได้ด้วย ไม่ใช่แค่เจ้าของหรือ admin
    if current.role not in ("admin", "staff") and booking.user_id != current.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์เข้าถึงการจองนี้")


@router.get("/timeslots", response_model=list[TimeslotRead])
def list_timeslots(session: Session = Depends(get_session)):
    query = (
        select(Timeslot)
        .where(Timeslot.is_available == True)  # noqa: E712
        .where(Timeslot.datetime > datetime.utcnow())
        .order_by(Timeslot.datetime)
    )
    return session.exec(query).all()


# แอดมินต้องเห็นรอบเวลาทั้งหมด รวมที่จองไปแล้ว/หมดอายุแล้ว เพื่อจัดการได้ครบ ไม่ใช่แค่ที่ว่างเหมือน list_timeslots
@router.get("/timeslots/all", response_model=list[TimeslotRead])
def list_all_timeslots(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    return session.exec(select(Timeslot).order_by(Timeslot.datetime)).all()


@router.post("/timeslots", response_model=TimeslotRead, status_code=status.HTTP_201_CREATED)
def create_timeslot(data: TimeslotCreate, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    timeslot = Timeslot(datetime=data.datetime, technician_name=data.technician_name, is_available=True)
    session.add(timeslot)
    session.commit()
    session.refresh(timeslot)
    return timeslot


@router.put("/timeslots/{timeslot_id}", response_model=TimeslotRead)
def update_timeslot(
    timeslot_id: int,
    data: TimeslotUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    timeslot = session.get(Timeslot, timeslot_id)
    if timeslot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบช่วงเวลา")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(timeslot, field, value)

    session.add(timeslot)
    session.commit()
    session.refresh(timeslot)
    return timeslot


@router.delete("/timeslots/{timeslot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeslot(timeslot_id: int, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    timeslot = session.get(Timeslot, timeslot_id)
    if timeslot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบช่วงเวลา")

    # เช็ค booking ที่เคยผูกกับรอบเวลานี้ (รวมที่ยกเลิกไปแล้ว) เพราะ FK ยังอ้างถึงอยู่ ลบไม่ได้จริงๆ
    existing_booking = session.exec(select(Booking).where(Booking.timeslot_id == timeslot_id)).first()
    if existing_booking is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "ลบไม่ได้ เพราะรอบเวลานี้เคยมีการจองผูกอยู่")

    session.delete(timeslot)
    session.commit()


@router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    item = session.get(Item, data.item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบรายการของเก่า")
    if item.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์ใช้รายการนี้")
    if item.status != "assessed":
        raise HTTPException(status.HTTP_409_CONFLICT, "รายการนี้ถูกจองไปแล้วหรือยังไม่ผ่านการประเมิน")

    product = None
    if data.product_id is not None:
        product = session.get(Product, data.product_id)
        if product is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบสินค้า")

    timeslot = session.get(Timeslot, data.timeslot_id)
    if timeslot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบช่วงเวลา")
    if not timeslot.is_available or timeslot.datetime <= datetime.utcnow():
        raise HTTPException(status.HTTP_409_CONFLICT, "ช่วงเวลานี้เพิ่งถูกจอง กรุณาเลือกใหม่")

    total_price = (product.price if product else 0) - item.estimated_price

    booking = Booking(
        user_id=user.id,
        item_id=item.id,
        product_id=data.product_id,
        timeslot_id=data.timeslot_id,
        address=data.address,
        total_price=total_price,
        status="pending",
    )
    timeslot.is_available = False
    item.status = "scheduled"

    session.add(booking)
    session.add(timeslot)
    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "ช่วงเวลานี้เพิ่งถูกจอง กรุณาเลือกใหม่")

    session.refresh(booking)
    return booking


@router.get("/bookings", response_model=list[BookingRead])
def list_bookings(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role == "admin":
        return session.exec(select(Booking)).all()
    return session.exec(select(Booking).where(Booking.user_id == user.id)).all()


@router.get("/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    booking = session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการจอง")
    _require_owner_or_admin(booking, user)
    return booking


@router.get("/bookings/{booking_id}/detail", response_model=BookingDetailRead)
def get_booking_detail(booking_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    booking = session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการจอง")
    _require_access(booking, user)

    item = session.get(Item, booking.item_id)
    product = session.get(Product, booking.product_id) if booking.product_id is not None else None
    timeslot = session.get(Timeslot, booking.timeslot_id)
    owner = session.get(User, booking.user_id)
    if item is None or timeslot is None or owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ข้อมูลการจองไม่ครบถ้วน")

    return BookingDetailRead(
        id=booking.id,
        address=booking.address,
        total_price=booking.total_price,
        status=booking.status,
        created_at=booking.created_at,
        item=ItemRead.model_validate(item, from_attributes=True),
        product=ProductRead.model_validate(product, from_attributes=True) if product else None,
        timeslot=TimeslotRead.model_validate(timeslot, from_attributes=True),
        user=UserRead.model_validate(owner, from_attributes=True),
    )


@router.put("/bookings/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(booking_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    booking = session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการจอง")
    _require_owner_or_admin(booking, user)

    booking.status = "cancelled"
    timeslot = session.get(Timeslot, booking.timeslot_id)
    if timeslot is not None:
        timeslot.is_available = True
        session.add(timeslot)

    item = session.get(Item, booking.item_id)
    if item is not None:
        item.status = "assessed"
        session.add(item)

    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


@router.put("/bookings/{booking_id}/status", response_model=BookingRead)
def update_booking_status(
    booking_id: int,
    data: BookingStatusUpdate,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_staff),
):
    booking = session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการจอง")

    booking.status = data.status
    session.add(booking)

    new_item_status = ITEM_STATUS_ON_BOOKING_STATUS.get(data.status)
    if new_item_status:
        item = session.get(Item, booking.item_id)
        if item is not None:
            item.status = new_item_status
            session.add(item)

    session.commit()
    session.refresh(booking)
    return booking
