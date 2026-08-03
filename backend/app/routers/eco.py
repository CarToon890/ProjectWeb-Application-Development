from collections import Counter

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import Item, User
from app.schemas import EcoStats

router = APIRouter()


def _build_stats(items: list[Item]) -> EcoStats:
    by_category = Counter(item.furniture_type for item in items)
    return EcoStats(
        total_items=len(items),
        total_co2_saved_kg=sum(item.co2_saved_kg for item in items),
        by_category=dict(by_category),
    )


@router.get("/eco-stats", response_model=EcoStats)
def eco_stats(session: Session = Depends(get_session)):
    items = session.exec(select(Item).where(Item.status == "donated")).all()
    return _build_stats(items)


@router.get("/eco-stats/me", response_model=EcoStats)
def eco_stats_me(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    items = session.exec(
        select(Item).where(Item.status == "donated").where(Item.user_id == user.id)
    ).all()
    return _build_stats(items)
