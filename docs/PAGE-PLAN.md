# แผนผังหน้าเว็บและสถาปัตยกรรมระบบ — The Disposal Guilt

> **เอกสารภาพรวมระบบและหน้าเว็บทั้งหมด (อัปเดตสถานะล่าสุด: สิงหาคม 2026)**  
> โครงสร้างระบบ: **Frontend** = Vanilla HTML5 + CSS3 (Design System v3.0) + Modern JavaScript + Lucide Icons | **Backend** = FastAPI + SQLModel + PostgreSQL 16 + Alembic Migration | **Auth** = JWT ใน `localStorage` + Role-based Access Control (`user`, `staff`, `admin`)

---

## 1. สรุปสถานะการพัฒนาภาพรวม (Implementation Status)

ระบบพัฒนาเสร็จสมบูรณ์ **100% ครบทุกโมดูล** (รวม 23 หน้า HTML + 4 Shared JS Modules + 1 Central CSS Design System + ระบบ Alembic Migration):

```text
สถานะการทำงาน:
[COMPLETED] Design System v3.0 (Navy Palette + Dark Mode + 8pt Spacing Scale + 12-Column Grid)
[COMPLETED] 100% SVG Lucide Icons (ไม่มี Emoji ในระบบ)
[COMPLETED] Trade-in 4-Step Stepper Wizard Component
[COMPLETED] 2-Column Split Layouts บนหน้า Checkout / Product Detail / Booking Detail
[COMPLETED] Customer Flow ครบวงจร (ประเมิน -> ผลประเมิน -> เลือกของใหม่ -> นัดวันเวลา -> จองสำเร็จ)
[COMPLETED] Staff Job Management & Digital Checklist
[COMPLETED] Admin Management Dashboard (การจอง, ของเก่า, สินค้า, รอบเวลา, ผู้ใช้)
[COMPLETED] Backend RESTful API & PostgreSQL Database Seed
[COMPLETED] Alembic Database Migration System (Auto-upgrade on startup + Baseline revision)
```

---

## 2. โครงสร้างหน้าเว็บทั้งหมด (Sitemap Overview - 23 หน้า)

```text
PUBLIC & AUTHENTICATION (เข้าถึงได้ทุกคน)
├── index.html ................... Modern SaaS Landing Page (Hero 2-col, Live Stats, 4-Step Process, Rich Footer)
├── pages/register.html .......... สมัครสมาชิก (Real-time check username)
└── pages/login.html ............. เข้าสู่ระบบ (Redirect อัตโนมัติตาม ?next=)

CUSTOMER FLOW (Role: user) — มี 4-Step Stepper Wizard นำทาง
├── pages/assessment-form.html ... [ขั้นตอนที่ 1] ถ่ายรูป & เลือกประเภท/สภาพ (พรีวิวราคา Real-time)
├── pages/assessment-result.html . [ขั้นตอนที่ 1] ผลการประเมินราคา + ส่วนลด Trade-in + สถิติ CO2
├── pages/products.html .......... [ขั้นตอนที่ 2] แคตตาล็อกของใหม่ + แถบส่วนลด Trade-in อัตโนมัติ
├── pages/product-detail.html .... [ขั้นตอนที่ 2] 2-Column Split Layout (สเปกสินค้า + Sticky Trade-in Summary)
├── pages/select-datetime.html ... [ขั้นตอนที่ 3] เลือกรอบวัน-เวลานัดหมายแบบ Calendar Grouped Cards
├── pages/checkout.html .......... [ขั้นตอนที่ 4] 2-Column Split Layout (ฟอร์มที่อยู่ + Sticky Order Summary)
├── pages/booking-success.html ... แจ้งเตือนการจองสำเร็จ พร้อมรหัสคำสั่งจอง
├── pages/booking-status.html .... รายการประวัติการจองทั้งหมดของผู้ใช้ (Card Grid + Status Border)
├── pages/booking-detail.html .... 2-Column Split (Vertical Timeline + รายละเอียด + ปุ่มยกเลิก)
├── pages/my-items.html .......... รายการของเก่าของฉันทั้งหมด (Card Grid + แก้ไขสภาพ/ลบ + ใช้ส่วนลด)
├── pages/eco-dashboard.html ..... สถิติสิ่งแวดล้อมส่วนบุคคล vs สถิติรวมทั้งระบบ + ปุ่ม Share
└── pages/profile.html ........... ข้อมูลส่วนตัว + ที่อยู่เริ่มต้น + ฟอร์มเปลี่ยนรหัสผ่าน

STAFF APP SHELL (Role: staff, mobile-first)
├── staff/jobs.html .............. ตารางงานช่าง (งานวันนี้ / งานที่กำลังจะถึง / ประวัติงาน) + ลิงก์ Google Maps
└── staff/checklist.html ......... Digital Checklist หน้างาน (เทียบรูปจริง + ตรวจสอบ 4 ข้อ + ถ่ายรูปผนัง + ปิดงาน)

ADMIN DASHBOARD APP SHELL (Role: admin, Container 1200px)
├── admin/index.html ............. Dashboard สรุปตัวเลขสถิติภาพรวม และการจองล่าสุด
├── admin/bookings.html .......... จัดการสถานะการจองทั้งหมดในระบบ (เชื่อมโยง Auto-status items)
├── admin/items.html ............. ตรวจสอบรายการของเก่าทั้งระบบ + แก้ไขประเภท/ราคา
├── admin/products.html .......... เพิ่ม ลบ แก้ไขแคตตาล็อกสินค้า + ปรับสต๊อก Real-time
├── admin/timeslots.html ......... จัดการรอบเวลานัดหมาย (สร้างเดี่ยว / สร้าง Bulk หลายวันพร้อมกัน)
└── admin/users.html ............. จัดการรายชื่อผู้ใช้และปรับเปลี่ยนสิทธิ์ (Role: user / staff / admin)

SHARED MODULES & DESIGN SYSTEM
├── css/main.css ................. Professional Design System v3.0 (Tokens, 8pt Grid, Dark Mode, Stepper, Split)
├── js/api.js .................... RESTful API Fetcher พร้อม Auto Bearer Token
├── js/auth.js ................... Token Manager, requireLogin(), requireRole(), handleLogout()
├── js/components.js ............. Navbar + Lucide, Dark Mode Toggle, renderStepper(), renderFooter(), Toast, Modal
└── js/flow.js ................... Trade-in Multi-step Session Storage State Manager
```

---

## 3. ตารางสรุปรายละเอียดของทุกหน้าและ API ที่เรียกใช้

| ลำดับ | ไฟล์ | สิทธิ์ที่ต้องใช้ | บทบาทในระบบ / Journey | API Endpoints ที่เรียกใช้ |
|---|---|:---:|---|---|
| 1 | `index.html` | Public | Landing Page แสดง Hero 2 คอลัมน์, Live Stats, 4-Step Process | `GET /api/eco-stats` |
| 2 | `pages/register.html` | Public | ฟอร์มสมัครสมาชิก พร้อมเช็ค Username ซ้ำแบบ Real-time | `POST /api/register`, `GET /api/check-username/{name}` |
| 3 | `pages/login.html` | Public | ฟอร์มเข้าสู่ระบบ รองรับการพาไปหน้าเดิมด้วย `?next=` | `POST /api/login` |
| 4 | `pages/assessment-form.html` | User | **[Step 1]** ส่งข้อมูลประเมินเฟอร์นิเจอร์เก่า พร้อมอัปโหลดรูป | `POST /api/items`, `POST /api/uploads` |
| 5 | `pages/assessment-result.html`| User | **[Step 1]** แสดงมูลค่าประเมิน และสถิติ CO2 ที่ช่วยโลกได้ | `GET /api/items/{id}` |
| 6 | `pages/products.html` | Public/User | **[Step 2]** เลือกซื้อสินค้าใหม่พร้อมคำนวณหักส่วนลด Trade-in | `GET /api/products`, `GET /api/items/{id}` |
| 7 | `pages/product-detail.html` | Public/User | **[Step 2]** 2-Column Split แสดงสเปกสินค้าคู่กับการ์ดคำนวณส่วนลด | `GET /api/products/{id}`, `GET /api/items/{id}` |
| 8 | `pages/select-datetime.html` | User | **[Step 3]** เลือกรอบวัน-เวลานัดหมายแบบ Grouped Day Cards | `GET /api/timeslots` |
| 9 | `pages/checkout.html` | User | **[Step 4]** 2-Column Split สรุปข้อมูลทั้งหมด และบันทึกการจอง | `GET /api/items/{id}`, `GET /api/products/{id}`, `GET /api/timeslots/{id}`, `GET /api/me`, `POST /api/bookings` |
| 10 | `pages/booking-success.html` | User | แสดงผลการจองสำเร็จและรหัสคำสั่งจอง | `GET /api/bookings/{id}/detail` |
| 11 | `pages/booking-status.html` | User | แสดงประวัติการจองทั้งหมด พร้อมแถบสีสถานะ | `GET /api/bookings` |
| 12 | `pages/booking-detail.html` | User | 2-Column Split แสดง Vertical Timeline และปุ่มยกเลิก | `GET /api/bookings/{id}/detail`, `PUT /api/bookings/{id}/cancel` |
| 13 | `pages/my-items.html` | User | รายการของเก่าของผู้ใช้ พร้อมฟังก์ชันแก้ไขประเภท/สภาพ หรือลบ | `GET /api/items`, `PUT /api/items/{id}`, `DELETE /api/items/{id}` |
| 14 | `pages/eco-dashboard.html` | User | 2-Column Comparison สถิติ CO2 ของตนเองเทียบกับสถิติรวมของระบบ | `GET /api/eco-stats/me`, `GET /api/eco-stats` |
| 15 | `pages/profile.html` | User | แก้ไขข้อมูลส่วนตัว ที่อยู่ และฟอร์มเปลี่ยนรหัสผ่าน | `GET /api/me`, `PUT /api/me`, `POST /api/change-password` |
| 16 | `staff/jobs.html` | Staff/Admin | ตารางงานช่าง แยกงานวันนี้ / งานในอนาคต / ประวัติงาน | `GET /api/staff/jobs` |
| 17 | `staff/checklist.html` | Staff/Admin | Digital Checklist หน้างาน (เทียบรูป + เช็ค 4 ข้อ + ถ่ายรูปผนัง) | `GET /api/bookings/{id}/detail`, `POST /api/uploads`, `PUT /api/bookings/{id}/status` |
| 18 | `admin/index.html` | Admin | Dashboard สรุปยอดสถิติภาพรวม คำสั่งจองล่าสุด | `GET /api/bookings`, `GET /api/items`, `GET /api/eco-stats` |
| 19 | `admin/bookings.html` | Admin | ตารางจัดการสถานะการจองทั้งหมด | `GET /api/bookings`, `GET /api/items`, `GET /api/products`, `GET /api/users`, `PUT /api/bookings/{id}/status` |
| 20 | `admin/items.html` | Admin | ตารางตรวจสอบของเก่าทั้งหมดในระบบ + แก้ไขประเภท/ราคา | `GET /api/items`, `PUT /api/items/{id}` |
| 21 | `admin/products.html` | Admin | เพิ่ม/แก้ไข/ลบสินค้าในแคตตาล็อก และปรับจำนวนสต๊อก | `GET /api/products`, `POST /api/products`, `PUT /api/products/{id}`, `DELETE /api/products/{id}` |
| 22 | `admin/timeslots.html` | Admin | สร้างรอบเวลานัดหมาย (สร้างเดี่ยว และสร้าง Bulk หลายวัน) | `GET /api/timeslots/all`, `POST /api/timeslots`, `PUT /api/timeslots/{id}`, `DELETE /api/timeslots/{id}` |
| 23 | `admin/users.html` | Admin | ตารางจัดการผู้ใช้ ค้นหา เปลี่ยนสิทธิ์ (Role) และ Pagination | `GET /api/users`, `PUT /api/users/{id}/role` |

---

## 4. ข้อมูลจำเพาะของระบบ Design System (Design Tokens)

### 4.1 ชุดสีหลัก (Color Palette)
- **Primary Navy Accent**: `#1e3a5f` (Light) / `#60a5fa` (Dark)
- **Success / Eco Green**: `#059669` (Light) / `#34d399` (Dark)
- **Danger Red**: `#dc2626` (Light) / `#f87171` (Dark)
- **Warning Amber**: `#d97706` (Light) / `#fbbf24` (Dark)
- **Background**: `#f3f5f8` (Light) / `#090d16` (Dark)
- **Surface**: `#ffffff` (Light) / `#131927` (Dark)

### 4.2 ระบบระยะห่าง 8pt Spacing Scale
- `--sp-1`: `4px`
- `--sp-2`: `8px`
- `--sp-3`: `12px`
- `--sp-4`: `16px`
- `--sp-5`: `20px`
- `--sp-6`: `24px`
- `--sp-8`: `32px`
- `--sp-10`: `40px`
- `--sp-12`: `48px`
- `--sp-16`: `64px`

### 4.3 ขนาดความกว้างหน้าจอ (Containers)
- `.container-xl`: `1200px` (Landing Page, Admin Dashboard, Data Tables)
- `.container-lg`: `1024px` (2-Column Split Flows, Product Detail, Checkout)
- `.container-md`: `768px` (ฟอร์มขนาดกลาง, ตารางงานช่าง)
- `.container-sm`: `520px` (Authentication, Dialogs, Success Cards)

---

## 5. สถาปัตยกรรม Database & Alembic Migrations

- **Database Engine**: PostgreSQL 16
- **Schema Management**: SQLModel (`app/models.py`)
- **Migration Framework**: Alembic 1.13+
- **Lifecycle Integration**: เมื่อรัน Container ระบบจะเรียก `database.run_migrations()` ซึ่งสั่ง `alembic upgrade head` อัตโนมัติก่อนเข้าสู่ขั้นตอนการ Seed ข้อมูล
- **Migration Versions**:
  - `0001_initial_baseline.py`: Baseline เริ่มต้นครอบคลุมทั้ง 5 ตารางหลัก (`user`, `item`, `product`, `timeslot`, `booking`) พร้อม Foreign Keys และ Indexes
