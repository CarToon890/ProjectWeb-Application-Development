from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.auth import get_current_admin, get_current_user
from app.database import get_session
from app.models import Booking, Item, Product, Timeslot, User
from app.schemas import BookingCreate, BookingRead, BookingStatusUpdate, TimeslotRead

router = APIRouter()

# booking status ที่เข้ามาแล้ว item ควรอัปเดตสถานะตามไปด้วย
ITEM_STATUS_ON_BOOKING_STATUS = {
    "in_transit": "picked_up",
    "completed": "donated",
}


def _require_owner_or_admin(booking: Booking, current: User) -> None:
    if current.role != "admin" and booking.user_id != current.id:
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
    admin: User = Depends(get_current_admin),
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
