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
│   │   ├── auth.py              # hash password, create/verify JWT, get_current_user/admin/staff
│   │   ├── seed.py              # ใส่ข้อมูลตั้งต้น (products, timeslots, user admin/staff)
│   │   └── routers/
│   │       ├── auth.py          # register / login / logout / change-password / check-username
│   │       ├── users.py         # /me, CRUD user, เปลี่ยน role (admin เท่านั้น)
│   │       ├── items.py         # เฟอร์นิเจอร์เก่าที่ส่งประเมิน
│   │       ├── products.py      # ของใหม่ในร้าน + CRUD (admin)
│   │       ├── bookings.py      # timeslots (list/CRUD) + การจอง + booking detail
│   │       ├── staff.py         # งานของช่างที่ล็อกอินอยู่ (/api/staff/jobs)
│   │       ├── uploads.py       # อัปโหลดรูปภาพ (เก็บใน frontend/uploads/)
│   │       └── eco.py           # สถิติสิ่งแวดล้อม
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Landing page
│   ├── css/
│   │   └── main.css             # CSS variables + component กลาง (nav, card, btn, badge, modal, table ฯลฯ)
│   ├── js/
│   │   ├── api.js               # apiFetch() + ฟังก์ชันเรียก API ทุกตัว (แนบ Bearer token อัตโนมัติ)
│   │   ├── auth.js              # จัดการ token/role, requireLogin(), requireRole(), handleLogout()
│   │   ├── components.js        # renderNav() (ตาม role), renderFooter(), toast(), confirmDialog()
│   │   └── flow.js              # เก็บ state ระหว่างขั้นตอนจอง (item/product/timeslot) ใน sessionStorage
│   ├── pages/                   # หน้าฝั่งลูกค้า (role: user)
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── assessment-form.html     # ประเมินของเก่า (เลือกประเภท/สภาพ, อัปโหลดรูป, พรีวิวราคา)
│   │   ├── assessment-result.html   # ผลประเมิน + ที่มาของราคา
│   │   ├── my-items.html            # ของเก่าของฉัน (แก้ไข/ลบ)
│   │   ├── products.html            # เลือกของใหม่
│   │   ├── product-detail.html      # รายละเอียดสินค้า + คำนวณส่วนลด
│   │   ├── select-datetime.html     # เลือกวัน-เวลานัดหมาย
│   │   ├── checkout.html            # สรุปก่อนยืนยัน + สร้างการจองจริง
│   │   ├── booking-success.html     # จองสำเร็จ
│   │   ├── booking-status.html      # รายการจองทั้งหมดของฉัน
│   │   ├── booking-detail.html      # รายละเอียดการจอง + timeline + ยกเลิก
│   │   ├── eco-dashboard.html       # สถิติ CO2 + เทียบเท่าปลูกต้นไม้ + แชร์
│   │   └── profile.html             # ข้อมูลส่วนตัว + เปลี่ยนรหัสผ่าน + ลิงก์เข้าหลังบ้าน (ถ้าเป็น admin)
│   ├── staff/                   # หน้าฝั่งช่างขนส่ง (role: staff, mobile-first)
│   │   ├── jobs.html            # งานที่ได้รับมอบหมาย (วันนี้ / กำลังจะถึง / เสร็จแล้ว)
│   │   └── checklist.html       # Digital Checklist เทียบรูป + อัปเดตสถานะงาน
│   ├── admin/                   # หน้าฝั่งแอดมิน (role: admin)
│   │   ├── index.html           # Dashboard สรุปตัวเลข
│   │   ├── bookings.html        # จัดการสถานะการจองทั้งหมด
│   │   ├── items.html           # ของเก่าทั้งระบบ
│   │   ├── products.html        # CRUD สินค้า + จัดการสต๊อก
│   │   ├── timeslots.html       # CRUD รอบเวลา (สร้างเดี่ยว/สร้างหลายวันพร้อมกัน)
│   │   └── users.html           # จัดการผู้ใช้ + เปลี่ยน role + pagination
│   └── uploads/                 # ไฟล์รูปที่อัปโหลด (gitignore ไว้ ไม่ commit)
├── docs/
│   └── PAGE-PLAN.md             # แผนหน้าเว็บและลำดับ Phase การพัฒนา
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

   บัญชีทดสอบที่ seed ไว้ให้แล้ว:

   | Role | Username | Password |
   |---|---|---|
   | admin | `admin` | `admin1234` |
   | staff (ทีมช่าง A) | `staff` | `staff1234` |

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
- **Users:** `/api/me`, `/api/users` (list มี pagination), `/api/users/{id}`, `/api/users/{id}/role` (admin)
- **Items (ของเก่า):** `/api/items` (CRUD), รายการ/สถานะกรองตาม role อัตโนมัติ
- **Products (ของใหม่):** `/api/products` (CRUD — เขียนได้เฉพาะ admin)
- **Bookings:** `/api/timeslots` (list ที่ว่าง), `/api/timeslots/all` + CRUD (admin), `/api/bookings`, `/api/bookings/{id}/detail`, `/api/bookings/{id}/cancel`, `/api/bookings/{id}/status` (staff/admin)
- **Staff:** `/api/staff/jobs` — งานของช่างที่ล็อกอินอยู่
- **Uploads:** `/api/uploads` — อัปโหลดรูปภาพ คืน URL ให้ใช้กับ `photo_url`
- **Eco stats:** `/api/eco-stats`, `/api/eco-stats/me`

### สิทธิ์การใช้งาน (role)

| Role | เข้าถึงได้ |
|---|---|
| `user` (ลูกค้า) | ประเมินของเก่า, จอง, ดูของเก่า/การจองของตัวเอง |
| `staff` (ช่าง) | ดูงานที่ได้รับมอบหมาย (จับคู่ผ่านชื่อ-นามสกุลกับ `Timeslot.technician_name`), อัปเดตสถานะการจอง |
| `admin` | เข้าถึงได้ทุก endpoint รวมจัดการ products/timeslots/users และดูข้อมูลของทุกคน |
