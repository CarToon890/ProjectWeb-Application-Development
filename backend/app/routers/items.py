from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import Booking, Item, User
from app.schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter()

BASE_PRICE = {"sofa": 3000, "bed": 2500, "wardrobe": 2000, "table": 1500, "chair": 800, "shelf": 1000, "other": 500}
CONDITION_MULT = {"good": 0.5, "fair": 0.3, "poor": 0.1}
CO2_FACTOR = 0.012


def _calc(furniture_type: str, condition: str) -> tuple[int, float]:
    base = BASE_PRICE[furniture_type]
    estimated_price = int(base * CONDITION_MULT[condition])
    co2_saved_kg = base * CO2_FACTOR
    return estimated_price, co2_saved_kg


def _require_owner_or_admin(item: Item, current: User) -> None:
    if current.role != "admin" and item.user_id != current.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์เข้าถึงรายการนี้")


@router.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    estimated_price, co2_saved_kg = _calc(data.furniture_type, data.condition)
    item = Item(
        user_id=user.id,
        furniture_type=data.furniture_type,
        condition=data.condition,
        description=data.description,
        photo_url=data.photo_url,
        estimated_price=estimated_price,
        co2_saved_kg=co2_saved_kg,
        status="assessed",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/items", response_model=list[ItemRead])
def list_items(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role == "admin":
        return session.exec(select(Item)).all()
    return session.exec(select(Item).where(Item.user_id == user.id)).all()


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบรายการ")
    _require_owner_or_admin(item, user)
    return item


@router.put("/items/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    data: ItemUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบรายการ")
    _require_owner_or_admin(item, user)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    if "furniture_type" in updates or "condition" in updates:
        item.estimated_price, item.co2_saved_kg = _calc(item.furniture_type, item.condition)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบรายการ")
    _require_owner_or_admin(item, user)

    # เช็คทุก booking ที่เคยผูกกับรายการนี้ (รวมที่ยกเลิกไปแล้ว) เพราะ FK ยังอ้างถึงอยู่ ลบไม่ได้จริงๆ
    existing_booking = session.exec(select(Booking).where(Booking.item_id == item_id)).first()
    if existing_booking is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "ลบไม่ได้ เพราะรายการนี้เคยมีการจองผูกอยู่")

    session.delete(item)
    session.commit()
