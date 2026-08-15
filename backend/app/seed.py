from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.auth import hash_password
from app.models import Product, Timeslot, User

PRODUCTS = [
    {"name": "โซฟา 3 ที่นั่ง รุ่น Nordic", "category": "sofa", "price": 12900, "image_url": "/static/products/sofa1.jpg", "stock": 5},
    {"name": "โซฟาเบด พับได้ รุ่น Compact", "category": "sofa", "price": 8900, "image_url": "/static/products/sofa2.jpg", "stock": 8},
    {"name": "โต๊ะทานข้าว 4 ที่นั่ง", "category": "table", "price": 6500, "image_url": "/static/products/table1.jpg", "stock": 6},
    {"name": "โต๊ะทำงานไม้โอ๊ค", "category": "table", "price": 4200, "image_url": "/static/products/table2.jpg", "stock": 10},
    {"name": "เก้าอี้สำนักงาน เออร์โกโนมิก", "category": "chair", "price": 3200, "image_url": "/static/products/chair1.jpg", "stock": 15},
    {"name": "เก้าอี้ทานข้าว (เซ็ต 4 ตัว)", "category": "chair", "price": 4800, "image_url": "/static/products/chair2.jpg", "stock": 7},
    {"name": "เตียงนอน 6 ฟุต พร้อมฐาน", "category": "bed", "price": 15900, "image_url": "/static/products/bed1.jpg", "stock": 4},
    {"name": "ตู้เสื้อผ้าบานเลื่อน 4 บาน", "category": "wardrobe", "price": 9900, "image_url": "/static/products/wardrobe1.jpg", "stock": 5},
    {"name": "ชั้นวางหนังสือ 5 ชั้น", "category": "shelf", "price": 2500, "image_url": "/static/products/shelf1.jpg", "stock": 12},
    {"name": "ชั้นวางรองเท้า", "category": "shelf", "price": 1500, "image_url": "/static/products/shelf2.jpg", "stock": 20},
]

TECHNICIANS = ["ทีมช่าง A", "ทีมช่าง B", "ทีมช่าง C"]


def seed_data(session: Session) -> None:
    if not session.exec(select(Product)).first():
        for data in PRODUCTS:
            session.add(Product(**data))

    if not session.exec(select(Timeslot)).first():
        base = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        slot_count = 0
        for day in range(6):
            for hour in (9, 13, 15):
                session.add(
                    Timeslot(
                        datetime=base + timedelta(days=day, hours=hour - base.hour),
                        technician_name=TECHNICIANS[slot_count % len(TECHNICIANS)],
                        is_available=True,
                    )
                )
                slot_count += 1

    if not session.exec(select(User).where(User.username == "admin")).first():
        session.add(
            User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin1234"),
                full_name="System Admin",
                role="admin",
            )
        )

    if not session.exec(select(User).where(User.username == "staff")).first():
        session.add(
            User(
                username="staff",
                email="staff@example.com",
                password_hash=hash_password("staff1234"),
                full_name="ทีมช่าง A",
                role="staff",
            )
        )

    session.commit()
