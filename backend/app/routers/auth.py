import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_session
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsernameAvailable,
    UserRead,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    stage = "username_lookup"
    try:
        if session.exec(select(User).where(User.username == data.username)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "username นี้ถูกใช้ไปแล้ว")

        stage = "email_lookup"
        if session.exec(select(User).where(User.email == data.email)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "email นี้ถูกใช้ไปแล้ว")

        stage = "password_hash"
        password_hash = hash_password(data.password)

        stage = "user_create"
        user = User(
            username=data.username,
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
        )

        stage = "database_commit"
        session.add(user)
        session.commit()

        stage = "database_refresh"
        session.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as exc:
        # Record only the operation and exception class; never log submitted
        # registration fields, password hashes, or database parameters.
        logger.error("Registration failed at stage=%s exception=%s", stage, type(exc).__name__)
        raise


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "username หรือ password ไม่ถูกต้อง")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"message": "ออกจากระบบสำเร็จ"}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "old_password ไม่ถูกต้อง")

    user.password_hash = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"message": "เปลี่ยนรหัสผ่านสำเร็จ"}


@router.get("/check-username/{name}", response_model=UsernameAvailable)
def check_username(name: str, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.username == name)).first()
    return UsernameAvailable(available=exists is None)
