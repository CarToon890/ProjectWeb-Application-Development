from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.auth import get_current_admin, get_current_user
from app.database import get_session
from app.models import User
from app.schemas import UserRead, UserUpdate

router = APIRouter()


def _require_owner_or_admin(target_id: int, current: User) -> None:
    if current.role != "admin" and current.id != target_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์เข้าถึงข้อมูลผู้ใช้คนนี้")


@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserRead])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    offset = (page - 1) * limit
    return session.exec(select(User).offset(offset).limit(limit)).all()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session), current: User = Depends(get_current_user)):
    _require_owner_or_admin(user_id, current)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบผู้ใช้")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    _require_owner_or_admin(user_id, current)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบผู้ใช้")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบผู้ใช้")
    session.delete(user)
    session.commit()
