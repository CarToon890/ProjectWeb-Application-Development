# The Disposal Guilt

> แพลตฟอร์มเฟอร์นิเจอร์ Trade-in: "ทิ้งก็เสียดาย ขายก็ลำบาก"
> ผู้ใช้ถ่ายรูปเฟอร์นิเจอร์เก่าส่งประเมินราคา ได้คูปองส่วนลดไปซื้อของใหม่ นัดช่างมารับของเก่า/ส่งของใหม่ในรอบเดียว

## สมาชิกกลุ่ม

- นายสุรชัช ศาลาน้อย 67160378
- นายจิรัฐติกุล งามขำ 67160322

---

## Tech Stack

| Layer | เทคโนโลยี |
|---|---|
| Frontend | HTML + CSS + JavaScript (ไม่ใช้ framework), เรียก API ด้วย `fetch()` |
| Backend | FastAPI (Python 3.12) |
| ORM | SQLModel |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| DB Admin | pgAdmin 4 |
| Orchestration | Docker Compose |

---

## โครงสร้างโปรเจกต์

```
ProjectWeb-Application-Development/
├── backend/
│   ├── app/
│   │   ├── main.py              # entry point, mount static, include routers, seed ตอน startup
│   │   ├── database.py          # engine + get_session()
│   │   ├── models.py            # SQLModel tables: User, Item, Product, Timeslot, Booking
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── auth.py              # hash password, create/verify JWT, get_current_user/admin
│   │   ├── seed.py              # ใส่ข้อมูลตั้งต้น (products, timeslots, admin user)
│   │   └── routers/
│   │       ├── auth.py          # register / login / logout / change-password / check-username
│   │       ├── users.py         # /me, CRUD user
│   │       ├── items.py         # เฟอร์นิเจอร์เก่าที่ส่งประเมิน
│   │       ├── products.py      # ของใหม่ในร้าน
│   │       ├── bookings.py      # timeslots + การจอง
│   │       └── eco.py           # สถิติสิ่งแวดล้อม
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Landing page
│   ├── pages/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── assessment-form.html
│   │   ├── products.html
│   │   ├── select-datetime.html
│   │   ├── booking-status.html
│   │   ├── eco-dashboard.html
│   │   └── profile.html
│   └── js/
│       ├── api.js               # apiFetch() + ฟังก์ชันเรียก API ทุกตัว (แนบ Bearer token อัตโนมัติ)
│       └── auth.js              # จัดการ token, requireLogin(), handleLogout()
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.MD
```

---

## วิธีติดตั้งและรัน

### สิ่งที่ต้องมี

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (เปิดโปรแกรมทิ้งไว้ก่อนรันคำสั่ง)
- [Git](https://git-scm.com/)

### ขั้นตอน

1. Clone โปรเจกต์

   ```bash
   git clone https://github.com/CarToon890/ProjectWeb-Application-Development.git
   cd ProjectWeb-Application-Development
   ```

2. สร้างไฟล์ `.env` จาก `.env.example` (ค่า default ใช้รันในเครื่องได้เลย ไม่ต้องแก้ก็ได้)

   ```bash
   cp .env.example .env
   ```

3. รันทั้งระบบด้วย Docker Compose

   ```bash
   docker compose up --build
   ```

   รอจน log ขึ้นประมาณนี้ (แปลว่าใช้งานได้แล้ว):

   ```
   web-1  | INFO:     Application startup complete.
   ```

   รันครั้งแรกจะช้าหน่อยเพราะต้อง build image + ดึง Postgres/pgAdmin ครั้งถัดไปจะเร็วขึ้นมาก ถ้าอยากรันแบบไม่บล็อก terminal ใส่ `-d` ต่อท้าย

4. เปิดใช้งาน

   | URL | ใช้ทำอะไร |
   |---|---|
   | http://localhost:8000/index.html | หน้าเว็บ (landing page) |
   | http://localhost:8000/docs | Swagger UI — ทดสอบทุก endpoint |
   | http://localhost:5050 | pgAdmin (login: `admin@admin.com` / `admin`) |

   บัญชี admin ที่ seed ไว้ให้แล้ว: username `admin` / password `admin1234`

5. ปิดระบบ

   ```bash
   docker compose down
   ```

   ข้อมูลใน DB จะยังอยู่ (เก็บใน volume `db_data`) จนกว่าจะรันด้วย `docker compose down -v` ถึงจะลบข้อมูลทิ้งด้วย

### คำสั่งที่ใช้บ่อย

```bash
docker compose up        # รันทั้งระบบ
docker compose down      # ปิด
docker compose logs -f web   # ดู log ของ backend
```

---

## Endpoints หลัก

ดูรายละเอียดทั้งหมดพร้อมทดสอบได้ที่ `/docs` (Swagger UI) หลังรันระบบแล้ว ครอบคลุม:

- **Auth:** `/api/register`, `/api/login`, `/api/logout`, `/api/change-password`, `/api/check-username/{name}`
- **Users:** `/api/me`, `/api/users`
- **Items (ของเก่า):** `/api/items`
- **Products (ของใหม่):** `/api/products`
- **Bookings:** `/api/timeslots`, `/api/bookings`
- **Eco stats:** `/api/eco-stats`, `/api/eco-stats/me`
