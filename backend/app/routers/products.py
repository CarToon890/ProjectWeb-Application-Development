from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Product
from app.schemas import ProductRead

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
