from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_admin
from app.database import get_session
from app.models import Booking, Product, User
from app.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
def list_products(category: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    return session.exec(query).all()


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบสินค้า")
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    product = Product(**data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบสินค้า")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบสินค้า")

    # เช็ค booking ที่เคยผูกกับสินค้านี้ (รวมที่ยกเลิกไปแล้ว) เพราะ FK ยังอ้างถึงอยู่ ลบไม่ได้จริงๆ
    existing_booking = session.exec(select(Booking).where(Booking.product_id == product_id)).first()
    if existing_booking is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "ลบไม่ได้ เพราะสินค้านี้เคยมีการจองผูกอยู่")

    session.delete(product)
    session.commit()
