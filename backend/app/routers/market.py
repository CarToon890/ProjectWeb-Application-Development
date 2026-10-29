from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field as PField
from sqlalchemy import or_
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import MarketChat, MarketListing, MarketMessage, MarketOrder, User

router = APIRouter()

class ListingIn(BaseModel):
    title: str = PField(min_length=2, max_length=120)
    furniture_type: str
    condition: str
    description: str = PField(min_length=1, max_length=3000)
    price: int = PField(gt=0)
    image_url: Optional[str] = None

class MessageIn(BaseModel):
    body: str = PField(min_length=1, max_length=2000)

class OrderIn(BaseModel):
    shipping_fee: int = PField(ge=0)
    address: str = PField(min_length=5, max_length=1000)
    payment_proof_url: str = PField(min_length=1)

class DecisionIn(BaseModel):
    reason: Optional[str] = None

class ShipmentIn(BaseModel):
    carrier: str = PField(min_length=1, max_length=120)
    tracking_number: str = PField(min_length=1, max_length=120)

class RefundIn(BaseModel):
    reason: str
    proof_url: str

def fail(code, msg):
    raise HTTPException(code, msg)

@router.get("/market/listings")
def listings(q: str = "", furniture_type: str = "", session: Session = Depends(get_session)):
    query = select(MarketListing).where(MarketListing.status == "available")
    if furniture_type: query = query.where(MarketListing.furniture_type == furniture_type)
    if q: query = query.where(or_(MarketListing.title.ilike(f"%{q}%"), MarketListing.description.ilike(f"%{q}%")))
    return session.exec(query.order_by(MarketListing.created_at.desc())).all()

@router.post("/market/listings", status_code=201)
def create_listing(data: ListingIn, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if data.furniture_type not in {"sofa","table","chair","bed","wardrobe","shelf","other"} or data.condition not in {"good","fair","poor"}: fail(400,"ประเภทหรือสภาพสินค้าไม่ถูกต้อง")
    row=MarketListing(**data.model_dump(),seller_id=user.id); session.add(row); session.commit(); session.refresh(row); return row

@router.get("/market/listings/mine")
def mine(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(MarketListing).where(MarketListing.seller_id==user.id).order_by(MarketListing.created_at.desc())).all()

@router.get("/market/listings/{listing_id}")
def listing_detail(listing_id:int, session:Session=Depends(get_session)):
    row=session.get(MarketListing,listing_id)
    if not row: fail(404,"ไม่พบประกาศ")
    seller=session.get(User,row.seller_id)
    return {"listing":row,"seller":{"id":seller.id,"full_name":seller.full_name}}

@router.post("/market/listings/{listing_id}/chats",status_code=201)
def start_chat(listing_id:int,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    item=session.get(MarketListing,listing_id)
    if not item: fail(404,"ไม่พบประกาศ")
    if item.seller_id==user.id: fail(400,"เริ่มแชตกับประกาศของตนเองไม่ได้")
    chat=session.exec(select(MarketChat).where(MarketChat.listing_id==listing_id,MarketChat.buyer_id==user.id)).first()
    if not chat:
        chat=MarketChat(listing_id=listing_id,buyer_id=user.id,seller_id=item.seller_id); session.add(chat); session.commit(); session.refresh(chat)
    return {"chat":chat}

def accessible_chat(chat_id, session, user):
    chat=session.get(MarketChat,chat_id)
    if not chat: fail(404,"ไม่พบห้องแชต")
    if user.id not in (chat.buyer_id,chat.seller_id): fail(403,"ไม่มีสิทธิ์เข้าถึงห้องแชต")
    return chat

@router.get("/market/chats")
def chats(session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    return session.exec(select(MarketChat).where(or_(MarketChat.buyer_id==user.id,MarketChat.seller_id==user.id)).order_by(MarketChat.created_at.desc())).all()

@router.get("/market/chats/{chat_id}/messages")
def messages(chat_id:int,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    chat=accessible_chat(chat_id,session,user)
    rows=session.exec(select(MarketMessage).where(MarketMessage.chat_id==chat_id).order_by(MarketMessage.created_at)).all()
    return {"messages":rows}

@router.post("/market/chats/{chat_id}/messages",status_code=201)
def send_message(chat_id:int,data:MessageIn,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    accessible_chat(chat_id,session,user)
    body=data.body.strip()
    if not body: fail(422,"ข้อความห้ามเว้นว่าง")
    row=MarketMessage(chat_id=chat_id,sender_id=user.id,body=body); session.add(row); session.commit(); session.refresh(row); return row

@router.post("/market/listings/{listing_id}/orders",status_code=201)
def create_order(listing_id:int,data:OrderIn,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    listing=session.exec(select(MarketListing).where(MarketListing.id==listing_id).with_for_update()).first()
    if not listing or listing.status!="available": fail(409,"ประกาศนี้ไม่พร้อมขายแล้ว")
    if listing.seller_id==user.id: fail(400,"ซื้อประกาศของตนเองไม่ได้")
    listing.status="reserved"; order=MarketOrder(listing_id=listing.id,buyer_id=user.id,seller_id=listing.seller_id,item_price=listing.price,shipping_fee=data.shipping_fee,address=data.address,payment_proof_url=data.payment_proof_url)
    session.add(order); session.add(listing); session.commit(); session.refresh(order); return order

@router.get("/market/orders")
def orders(session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    return session.exec(select(MarketOrder).where(or_(MarketOrder.buyer_id==user.id,MarketOrder.seller_id==user.id)).order_by(MarketOrder.created_at.desc())).all()

@router.put("/market/orders/{order_id}/payment")
def payment_decision(order_id:int,data:DecisionIn,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    order=session.get(MarketOrder,order_id)
    if not order: fail(404,"ไม่พบคำสั่งซื้อ")
    if order.seller_id!=user.id: fail(403,"เฉพาะผู้ขายตรวจสอบได้")
    if order.status!="awaiting_payment": fail(409,"สถานะคำสั่งซื้อไม่รองรับ")
    if data.reason:
        order.status="payment_rejected"; order.rejection_reason=data.reason
        listing=session.get(MarketListing,order.listing_id); listing.status="available"; session.add(listing)
    else: order.status="paid"
    session.add(order); session.commit(); session.refresh(order); return order

@router.put("/market/orders/{order_id}/shipment")
def shipment(order_id:int,data:ShipmentIn,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    order=session.get(MarketOrder,order_id)
    if not order: fail(404,"ไม่พบคำสั่งซื้อ")
    if order.seller_id!=user.id: fail(403,"เฉพาะผู้ขายจัดส่งได้")
    if order.status!="paid": fail(409,"ต้องยืนยันการชำระก่อน")
    order.carrier=data.carrier; order.tracking_number=data.tracking_number; order.status="shipped"; session.add(order); session.commit(); session.refresh(order); return order

@router.put("/market/orders/{order_id}/received")
def received(order_id:int,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    order=session.get(MarketOrder,order_id)
    if not order: fail(404,"ไม่พบคำสั่งซื้อ")
    if order.buyer_id!=user.id: fail(403,"เฉพาะผู้ซื้อยืนยันรับได้")
    if order.status!="shipped": fail(409,"คำสั่งซื้อยังไม่ได้จัดส่ง")
    order.status="completed"
    listing=session.get(MarketListing,order.listing_id)
    listing.status="sold"
    session.add(order); session.add(listing); session.commit(); session.refresh(order); return order

@router.put("/market/orders/{order_id}/refund")
def refund(order_id:int,data:RefundIn,session:Session=Depends(get_session),user:User=Depends(get_current_user)):
    order=session.get(MarketOrder,order_id)
    if not order: fail(404,"ไม่พบคำสั่งซื้อ")
    if order.seller_id!=user.id: fail(403,"เฉพาะผู้ขายบันทึกคืนเงินได้")
    if order.status not in ("paid","shipped"): fail(409,"สถานะคำสั่งซื้อไม่รองรับการคืนเงิน")
    order.status="refunded"; order.refund_reason=data.reason; order.refund_proof_url=data.proof_url
    listing=session.get(MarketListing,order.listing_id); listing.status="available"; session.add(listing); session.add(order); session.commit(); session.refresh(order); return order
