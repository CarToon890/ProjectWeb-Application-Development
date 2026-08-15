from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import get_current_staff
from app.database import get_session
from app.models import Booking, Item, Product, Timeslot, User
from app.schemas import BookingDetailRead, ItemRead, ProductRead, TimeslotRead, UserRead

router = APIRouter()


# งานของช่างคนที่ล็อกอินอยู่ — จับคู่ผ่าน Timeslot.technician_name == ชื่อ-นามสกุลของ staff
# (ระบบยังไม่มีความสัมพันธ์ user-technician โดยตรง ใช้ full_name เป็นตัวจับคู่แทน)
@router.get("/staff/jobs", response_model=list[BookingDetailRead])
def list_staff_jobs(session: Session = Depends(get_session), staff: User = Depends(get_current_staff)):
    query = (
        select(Booking)
        .join(Timeslot, Booking.timeslot_id == Timeslot.id)  # type: ignore[arg-type]
        .where(Timeslot.technician_name == staff.full_name)
        .where(Booking.status != "cancelled")
    )
    bookings = session.exec(query).all()

    results = []
    for booking in bookings:
        item = session.get(Item, booking.item_id)
        product = session.get(Product, booking.product_id) if booking.product_id is not None else None
        timeslot = session.get(Timeslot, booking.timeslot_id)
        owner = session.get(User, booking.user_id)
        if item is None or timeslot is None or owner is None:
            continue

        results.append(
            BookingDetailRead(
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
        )
    return results
