# แผนหน้าเว็บ — The Disposal Guilt

> เอกสารวางแผน (ยังไม่ลงมือโค้ด) สำหรับป้อนให้ Claude Code ทำต่อทีละ Phase
> ต่อยอดจากโครงเดิม: Frontend = HTML/CSS/JS ล้วน (ไม่ใช้ framework), Backend = FastAPI + SQLModel + PostgreSQL, Auth = JWT ใน localStorage
> อัปเดต: 15 ส.ค. 2026

---

## 1. สรุปสถานะปัจจุบัน

**หน้าที่มีอยู่แล้ว 9 หน้า**

```
frontend/index.html                    Landing
frontend/pages/register.html           สมัครสมาชิก
frontend/pages/login.html              เข้าสู่ระบบ
frontend/pages/assessment-form.html    ฟอร์มส่งประเมินของเก่า
frontend/pages/products.html           เลือกของใหม่
frontend/pages/select-datetime.html    เลือกรอบเวลา
frontend/pages/booking-status.html     สถานะการจอง
frontend/pages/eco-dashboard.html      แดชบอร์ดรักษ์โลก
frontend/pages/profile.html            โปรไฟล์
```

**ช่องว่างที่เจอ**

1. ยังไม่มีหน้าฝั่ง **Admin** เลย ทั้งที่ backend มี `get_current_admin` + `PUT /api/bookings/{id}/status` + `/api/users` CRUD รออยู่แล้ว
2. ยังไม่มีหน้า **Digital Checklist ของช่างขนส่ง** ซึ่งเป็น 1 ใน 5 Opportunity ของ User Journey
3. API หลายตัวยังไม่มีหน้าไหนเรียกใช้: `GET /api/items/{id}`, `PUT /api/items/{id}`, `DELETE /api/items/{id}`, `GET /api/products/{id}`, `GET /api/bookings/{id}`, `POST /api/change-password`
4. CSS เขียน inline ซ้ำกันทุกไฟล์ (~200 บรรทัดต่อหน้า) และ navbar ก็ copy กันไปมา → ควรแยกเป็นไฟล์กลางก่อนเพิ่มหน้าอีก 15+ หน้า ไม่งั้นแก้สีทีเดียวต้องไล่แก้ 25 ไฟล์
5. ไม่มี guard ตาม role — ตอนนี้ `requireLogin()` เช็คแค่ว่ามี token ไหม ถ้าเพิ่มหน้า admin/staff ต้องมี `requireRole('admin')`

---

## 2. Sitemap ภาพรวม

```
PUBLIC (ไม่ต้องล็อกอิน)
├── index.html ................... Landing / แคมเปญ
├── pages/how-it-works.html ...... วิธีใช้งาน 4 ขั้นตอน            [ใหม่ - optional]
├── pages/register.html
├── pages/login.html
└── pages/404.html ............... หน้าไม่พบ                      [ใหม่ - optional]

CUSTOMER (role: user)
├── pages/assessment-form.html ... ถ่ายรูป + กรอกข้อมูลของเก่า      [แก้]
├── pages/assessment-result.html . ผลตีราคา + CO2 + CTA           [ใหม่]
├── pages/my-items.html .......... ของเก่าของฉันทั้งหมด (CRUD)     [ใหม่]
├── pages/products.html .......... เลือกของใหม่ + ส่วนลด           [แก้]
├── pages/product-detail.html .... รายละเอียดสินค้า                [ใหม่]
├── pages/select-datetime.html ... เลือกรอบช่าง                    [แก้]
├── pages/checkout.html .......... สรุป + ที่อยู่ + ยืนยันจอง       [ใหม่]
├── pages/booking-success.html ... จองสำเร็จ                       [ใหม่]
├── pages/booking-status.html .... รายการจองทั้งหมด                [แก้]
├── pages/booking-detail.html .... รายละเอียด + timeline + ยกเลิก  [ใหม่]
├── pages/eco-dashboard.html ..... สถิติ CO2 + ปุ่ม Share          [แก้]
└── pages/profile.html ........... ข้อมูลส่วนตัว + เปลี่ยนรหัสผ่าน  [แก้]

STAFF (role: staff — ต้องเพิ่ม role ใหม่)
├── staff/jobs.html .............. งานที่ได้รับมอบหมายวันนี้        [ใหม่]
└── staff/checklist.html ......... เทียบรูปกับของจริง + อัปเดตงาน   [ใหม่]

ADMIN (role: admin)
├── admin/index.html ............. Dashboard สรุปตัวเลข            [ใหม่]
├── admin/bookings.html .......... จัดการสถานะการจอง              [ใหม่]
├── admin/items.html ............. ของเก่าทั้งระบบ                 [ใหม่]
├── admin/products.html .......... CRUD สินค้า                    [ใหม่]
├── admin/timeslots.html ......... CRUD รอบเวลา + ช่าง            [ใหม่]
└── admin/users.html ............. CRUD ผู้ใช้                     [ใหม่]

SHARED
├── css/main.css ................. ตัวแปรสี + layout + component   [ใหม่]
├── js/api.js .................... (มีแล้ว - เพิ่มฟังก์ชันใหม่)
├── js/auth.js ................... (มีแล้ว - เพิ่ม requireRole)
├── js/components.js ............. navbar / footer / toast         [ใหม่]
└── js/flow.js ................... เก็บ state ระหว่างขั้นตอนจอง     [ใหม่]
```

รวม **~27 หน้า** = เดิม 9 (แก้ 6) + ใหม่ 18

---

## 3. ตารางสรุปรายหน้า

| # | ไฟล์ | ระยะ Journey | สิทธิ์ | สถานะ | API ที่ใช้ |
|---|---|---|---|---|---|
| 1 | `index.html` | 1 Trigger | public | แก้ | – |
| 2 | `pages/how-it-works.html` | 1 Trigger | public | ใหม่ | – |
| 3 | `pages/register.html` | 1 Trigger | public | คงเดิม | `POST /api/register`, `GET /api/check-username/{name}` |
| 4 | `pages/login.html` | 1 Trigger | public | คงเดิม | `POST /api/login` |
| 5 | `pages/assessment-form.html` | 2 Assessment | user | แก้ | `POST /api/items` (+ upload) |
| 6 | `pages/assessment-result.html` | 2 Assessment | user | ใหม่ | `GET /api/items/{id}` |
| 7 | `pages/my-items.html` | 2 Assessment | user | ใหม่ | `GET/PUT/DELETE /api/items` |
| 8 | `pages/products.html` | 3 Decision | user | แก้ | `GET /api/products` |
| 9 | `pages/product-detail.html` | 3 Decision | user | ใหม่ | `GET /api/products/{id}` |
| 10 | `pages/select-datetime.html` | 3 Decision | user | แก้ | `GET /api/timeslots` |
| 11 | `pages/checkout.html` | 3 Decision | user | ใหม่ | `POST /api/bookings`, `GET /api/me` |
| 12 | `pages/booking-success.html` | 3 Decision | user | ใหม่ | `GET /api/bookings/{id}` |
| 13 | `pages/booking-status.html` | 4 Delivery | user | แก้ | `GET /api/bookings` |
| 14 | `pages/booking-detail.html` | 4 Delivery | user | ใหม่ | `GET /api/bookings/{id}`, `PUT .../cancel` |
| 15 | `pages/eco-dashboard.html` | 5 Post | user | แก้ | `GET /api/eco-stats/me`, `/api/eco-stats` |
| 16 | `pages/profile.html` | – | user | แก้ | `GET /api/me`, `PUT /api/users/{id}`, `POST /api/change-password` |
| 17 | `pages/404.html` | – | public | ใหม่ | – |
| 18 | `staff/jobs.html` | 4 Delivery | staff | ใหม่ | `GET /api/staff/jobs` ⚠️ |
| 19 | `staff/checklist.html` | 4 Delivery | staff | ใหม่ | `GET /api/bookings/{id}/detail` ⚠️, `PUT /api/bookings/{id}/status` |
| 20 | `admin/index.html` | – | admin | ใหม่ | `GET /api/eco-stats`, `/api/bookings`, `/api/items` |
| 21 | `admin/bookings.html` | – | admin | ใหม่ | `GET /api/bookings`, `PUT /api/bookings/{id}/status` |
| 22 | `admin/items.html` | – | admin | ใหม่ | `GET /api/items` |
| 23 | `admin/products.html` | – | admin | ใหม่ | `POST/PUT/DELETE /api/products` ⚠️ |
| 24 | `admin/timeslots.html` | – | admin | ใหม่ | `POST/PUT/DELETE /api/timeslots` ⚠️ |
| 25 | `admin/users.html` | – | admin | ใหม่ | `GET/PUT/DELETE /api/users` |

⚠️ = endpoint ยังไม่มี ต้องเพิ่มใน backend ก่อน (ดูข้อ 5)

---

## 4. รายละเอียดรายหน้า

### 4.1 ฝั่งลูกค้า

**`index.html` — Landing Page** *(แก้)*
- Hero สื่อสาร "รับจบในรอบเดียว: ส่งของใหม่ + ขนของเก่าออกให้"
- 3 การ์ดแก้ pain point: ไม่ต้องหาที่ทิ้ง / ไม่ต้องจ้างรถ / ได้ส่วนลด
- แถบตัวเลขสด ดึงจาก `GET /api/eco-stats` (ไม่ต้องล็อกอิน) — "ช่วยรับของเก่าไปแล้ว X ชิ้น ลด CO2 Y กก."
- Navbar เปลี่ยนตามสถานะ: ยังไม่ล็อกอิน → ปุ่ม เข้าสู่ระบบ/สมัคร | ล็อกอินแล้ว → เมนูผู้ใช้
- ปุ่ม CTA หลัก → ถ้าล็อกอินแล้วไป `assessment-form.html` ถ้ายังไม่ → `login.html?next=assessment-form.html`

**`pages/assessment-form.html` — AI Assessment** *(แก้)*
- อัปโหลดรูป + preview ทันที (ตอนนี้ `photo_url` รับแค่ string) → ต้องมี endpoint upload หรือ fallback เป็น URL/base64
- เลือกประเภท 7 แบบ (sofa/table/chair/bed/wardrobe/shelf/other) แสดงเป็นการ์ดไอคอน ไม่ใช่ dropdown
- เลือกสภาพ 3 ระดับ (good/fair/poor) พร้อมคำอธิบายว่าแต่ละระดับหน้าตายังไง — ลด pain point "กลัวโดนกดราคา"
- แสดง **ราคาประเมินคร่าวๆ แบบ realtime** ก่อนกดส่ง โดยคำนวณฝั่ง client ด้วยสูตรเดียวกับ backend (`BASE_PRICE × CONDITION_MULT`) เพื่อความโปร่งใส
- กดส่ง → `POST /api/items` → redirect ไป `assessment-result.html?id={item_id}`

**`pages/assessment-result.html` — ผลประเมิน** *(ใหม่)*
- แสดงรูป + ประเภท + สภาพ + **ส่วนลดที่ได้ (`estimated_price`)** ตัวใหญ่ + `co2_saved_kg`
- อธิบายที่มาของราคา (ราคาฐาน × ตัวคูณสภาพ)
- 2 ปุ่ม: "เลือกของใหม่เลย" → `products.html?item_id=` | "ประเมินชิ้นอื่นอีก" → กลับฟอร์ม

**`pages/my-items.html` — ของเก่าของฉัน** *(ใหม่)*
- ตาราง/การ์ดรายการทั้งหมดจาก `GET /api/items` + filter ตาม status
- Badge สถานะ 5 แบบ: `pending` / `assessed` / `scheduled` / `picked_up` / `donated`
- ปุ่มแก้ไข (`PUT`) และลบ (`DELETE`) — **ซ่อนปุ่มลบเมื่อ status = `scheduled`** เพราะ backend จะตอบ 400
- แก้ไขแล้วราคาจะถูกคำนวณใหม่อัตโนมัติ ต้องแจ้งผู้ใช้ด้วย

**`pages/products.html` — เลือกของใหม่** *(แก้)*
- Filter ตาม category (`GET /api/products?category=`)
- การ์ดสินค้าโชว์ ราคาเต็ม → ราคาหลังหักส่วนลด trade-in (สีเขียวถ้าเหลือจ่าย สีแดง/"ได้เงินคืน" ถ้าติดลบ)
- แถบส่วนลดค้างบนสุดตลอด: "คุณมีส่วนลด ฿X จาก [ชื่อของเก่า]"
- แสดง stock, ถ้า `stock = 0` ปุ่มเป็น disabled
- คลิกการ์ด → `product-detail.html?id=` | ปุ่มเลือก → `select-datetime.html`
- **หมายเหตุ:** ระบบเป็น 1 booking = 1 item + สินค้าใหม่อย่างมาก 1 ชิ้น (`product_id` เป็น optional เดี่ยว) → **ไม่ต้องทำตะกร้าหลายชิ้น** ถ้าอยากได้ตะกร้าจริงต้องแก้ schema ก่อน

**`pages/product-detail.html`** *(ใหม่)*
- รูปใหญ่ + รายละเอียด + สรุปการคำนวณ: ราคาสินค้า − ส่วนลดของเก่า = ยอดสุทธิ
- ปุ่ม "เลือกชิ้นนี้" → เก็บลง flow state → `select-datetime.html`

**`pages/select-datetime.html` — Smart Booking** *(แก้)*
- แสดง `GET /api/timeslots` (backend กรองเฉพาะที่ว่างและยังไม่ถึงกำหนดให้แล้ว) จัดกลุ่มเป็นวัน → ช่วงเวลา
- ย้ำข้อความ **"รอบเดียวจบ: ส่งของใหม่ + รับของเก่า"** ตรงนี้คือหัวใจของ pain point
- โชว์ชื่อช่างที่จะมา (`technician_name`)
- เลือกแล้ว → `checkout.html`

**`pages/checkout.html` — สรุปก่อนยืนยัน** *(ใหม่)*
- สรุป 3 บล็อก: ของเก่าที่จะให้รับ / ของใหม่ที่จะส่ง / วันเวลาและช่าง
- ช่องที่อยู่ — prefill จาก `GET /api/me` (`address`) แก้ไขได้
- สรุปยอด: ราคาสินค้า − ส่วนลด = `total_price` (ติดลบได้ = ทางร้านจ่ายคืน)
- กดยืนยัน → `POST /api/bookings`
- **ต้อง handle error 409** ("ช่วงเวลานี้เพิ่งถูกจอง") ให้เด้งกลับไปเลือกเวลาใหม่แบบสุภาพ ไม่ใช่ alert เปล่าๆ

**`pages/booking-success.html`** *(ใหม่)*
- เลขที่การจอง + สรุปนัดหมาย + ปุ่มไปดูสถานะ / กลับหน้าแรก

**`pages/booking-status.html` — รายการจอง** *(แก้)*
- `GET /api/bookings` แสดงเป็นการ์ด เรียงใหม่→เก่า
- Badge สถานะ 5 แบบ: `pending` / `confirmed` / `in_transit` / `completed` / `cancelled`
- คลิก → `booking-detail.html?id=`

**`pages/booking-detail.html`** *(ใหม่)*
- **Timeline แนวตั้ง** 4 ขั้น: รอยืนยัน → ยืนยันแล้ว → ช่างกำลังมา → เสร็จสิ้น
- รายละเอียดของเก่า/ของใหม่/เวลา/ที่อยู่/ยอดรวม
- ปุ่มยกเลิก (`PUT /api/bookings/{id}/cancel`) แสดงเฉพาะตอน status เป็น `pending`/`confirmed` + ต้องมี modal ยืนยันก่อน
- ปัจจุบันต้องยิง API หลายรอบเพื่อประกอบข้อมูล (booking → item → product → timeslot) — ควรเพิ่ม endpoint รวมให้ (ดูข้อ 5)

**`pages/eco-dashboard.html`** *(แก้)*
- ตัวเลขใหญ่: จำนวนชิ้นที่บริจาคแล้ว + CO2 รวม (`GET /api/eco-stats/me`)
- กราฟแท่งแยกตามประเภทเฟอร์นิเจอร์ (`by_category`) — วาดด้วย CSS ก็พอ ไม่ต้องลง Chart.js
- เทียบให้เห็นภาพ: "= ปลูกต้นไม้ N ต้น"
- เทียบยอดตัวเองกับยอดรวมทั้งระบบ (`GET /api/eco-stats`)
- **ปุ่ม Share** → Web Share API + fallback เป็น copy ข้อความ
- ⚠️ `eco-stats` นับเฉพาะ item ที่ status = `donated` เท่านั้น ถ้ายังไม่มีของครบวงจรหน้าจะว่าง → **ต้องออกแบบ empty state ให้ดี** ("ยังไม่มีข้อมูล เริ่มจากประเมินของชิ้นแรก")
- ส่วน "ของเก่าถูกนำไปไหน" ยังไม่มีข้อมูลใน DB → ต้องเพิ่ม field (ดูข้อ 5)

**`pages/profile.html`** *(แก้)*
- แก้ข้อมูลส่วนตัว (`PUT /api/users/{id}` — ใช้ id จาก `GET /api/me`)
- แท็บ/ส่วนเปลี่ยนรหัสผ่าน (`POST /api/change-password`) — ยังไม่มีหน้าไหนเรียกใช้เลย
- ลิงก์ไป my-items / booking-status / eco-dashboard
- ถ้า role = admin แสดงลิงก์เข้าหลังบ้าน

### 4.2 ฝั่งช่างขนส่ง (staff)

**`staff/jobs.html` — งานของฉัน** *(ใหม่)*
- รายการงานเรียงตามเวลานัด แยก "วันนี้ / กำลังจะถึง / เสร็จแล้ว"
- แต่ละการ์ด: เวลา, ชื่อลูกค้า, ที่อยู่, ของเก่าที่ต้องรับ, ของใหม่ที่ต้องส่ง
- ปุ่มเปิดแผนที่ (ลิงก์ Google Maps จากที่อยู่)

**`staff/checklist.html` — Digital Checklist** *(ใหม่)* ← หัวใจของ Journey ระยะ 4
- แสดง **รูปที่ลูกค้าอัปโหลด vs ช่องถ่ายรูปหน้างาน** วางคู่กันซ้าย-ขวา
- Checklist ติ๊ก: ประเภทตรงกับที่แจ้ง / สภาพตรง / ขนาดขนได้ / ทางเข้าออกผ่านได้
- ช่องหมายเหตุ + ถ่ายรูปสภาพผนัง/พื้นก่อนขน (กัน pain point "ช่างทำกำแพงรอย")
- ปุ่มอัปเดตสถานะ: รับของแล้ว (`in_transit`) → ส่งเสร็จ (`completed`)
- ⚠️ `PUT /api/bookings/{id}/status` ตอนนี้ล็อกไว้ที่ `get_current_admin` → ต้องเปิดให้ staff ด้วย
- ออกแบบเป็น **mobile-first** เพราะช่างใช้บนมือถือหน้างาน

### 4.3 ฝั่งแอดมิน

**`admin/index.html` — Dashboard** *(ใหม่)*
- การ์ดตัวเลข: จองวันนี้ / รอยืนยัน / ของรอประเมิน / CO2 รวมทั้งระบบ
- ตารางการจองล่าสุด 10 รายการ

**`admin/bookings.html`** *(ใหม่)*
- ตารางการจองทั้งหมด + filter ตามสถานะ
- Dropdown เปลี่ยนสถานะ (`PUT /api/bookings/{id}/status`)
- **ต้องเตือนในหน้าให้ชัด**: เปลี่ยนเป็น `in_transit` จะดันสถานะ item เป็น `picked_up` และ `completed` จะดันเป็น `donated` โดยอัตโนมัติ

**`admin/items.html`** *(ใหม่)*
- ของเก่าทั้งระบบ (admin เรียก `GET /api/items` จะได้ทุกคน) + filter ตาม status/ประเภท
- ดูรูปที่ลูกค้าส่งมา + แก้สภาพ/ราคาได้ผ่าน `PUT /api/items/{id}`

**`admin/products.html`** *(ใหม่)*
- ตารางสินค้า + ฟอร์มเพิ่ม/แก้/ลบ + จัดการ stock
- ⚠️ ต้องเพิ่ม `POST/PUT/DELETE /api/products` ก่อน (ตอนนี้มีแค่ GET)

**`admin/timeslots.html`** *(ใหม่)*
- ปฏิทินรอบเวลา + สร้างรอบใหม่ (ระบุวันเวลา + ชื่อช่าง) + สร้างเป็นชุดทีเดียวหลายวัน
- ⚠️ ต้องเพิ่ม `POST/PUT/DELETE /api/timeslots` ก่อน (ตอนนี้ seed มาจาก `seed.py` อย่างเดียว)

**`admin/users.html`** *(ใหม่)*
- ตารางผู้ใช้ + pagination (`GET /api/users?page=&limit=`) + แก้/ลบ + เปลี่ยน role

---

## 5. สิ่งที่ต้องเพิ่มฝั่ง Backend ก่อน (สำคัญ)

หน้าใหม่หลายหน้าจะทำไม่ได้ถ้า API ยังไม่มี — เรียงตามความจำเป็น

| # | สิ่งที่ต้องเพิ่ม | ทำไม | ความสำคัญ |
|---|---|---|---|
| 1 | `POST /api/uploads` รับไฟล์รูป คืน URL (เก็บใน `frontend/uploads/` หรือ static dir) | หน้า assessment + checklist ต้องอัปโหลดรูปจริง ตอนนี้ `photo_url` เป็นแค่ string ที่ผู้ใช้ต้องพิมพ์เอง | **สูงมาก** |
| 2 | เพิ่ม role `staff` ใน `Role` literal + dependency `get_current_staff` | หน้า staff ทั้ง 2 หน้าต้องใช้ | **สูง** |
| 3 | เปิดให้ staff เรียก `PUT /api/bookings/{id}/status` ได้ (ตอนนี้ admin เท่านั้น) | ช่างต้องกดอัปเดตหน้างาน | **สูง** |
| 4 | `GET /api/bookings/{id}/detail` คืน booking พร้อม item/product/timeslot/user ในก้อนเดียว | หน้า booking-detail และ checklist ต้องยิง 4 request ถ้าไม่มี | **สูง** |
| 5 | `GET /api/staff/jobs` งานของช่างคนที่ล็อกอิน (join ผ่าน `Timeslot.technician_name`) | หน้า staff/jobs | **กลาง** |
| 6 | `POST/PUT/DELETE /api/timeslots` (admin) | หน้า admin/timeslots | **กลาง** |
| 7 | `POST/PUT/DELETE /api/products` (admin) | หน้า admin/products | **กลาง** |
| 8 | เพิ่ม field `disposal_destination` + `disposal_note` ใน `Item` | Eco Dashboard ต้องตอบให้ได้ว่า "ของเก่าถูกส่งไปไหน" ซึ่งเป็น pain point ข้อ 5 ของ Journey ("กลัวโดนเอาไปทิ้งบ่อขยะ") — ตอนนี้ DB ไม่มีข้อมูลนี้เลย | **กลาง** |
| 9 | `GET /api/items?status=` filter | หน้า my-items / admin/items | **ต่ำ** |
| 10 | เพิ่ม field `checklist_note`, `before_photo_url` ใน `Booking` | เก็บผลจาก Digital Checklist | **ต่ำ** |

> ถ้าเวลาไม่พอ: ข้อ 1–4 คือขั้นต่ำที่ทำให้ระบบครบ Journey ทั้ง 5 ระยะ ส่วนข้อ 6–7 ข้ามได้โดยใช้ `seed.py` + pgAdmin แทน

---

## 6. งานโครงสร้างร่วม (ทำก่อนเพิ่มหน้าใหม่)

1. **แยก `frontend/css/main.css`** — ดึง CSS ที่ซ้ำใน 9 ไฟล์ออกมา ตั้ง CSS variables (`--bg: #f5f5f0`, `--ink: #1a1a1a`, `--accent: #3b7dd8`, `--ok: #16a34a`, `--danger: #b91c1c`) แล้วทำ component class กลาง: `.nav`, `.card`, `.btn`, `.badge`, `.form-field`, `.empty-state`
2. **`frontend/js/components.js`** — ฟังก์ชัน `renderNav()` / `renderFooter()` / `toast(msg, type)` แทนการ copy navbar ทุกไฟล์ นำเข้า nav ตาม role ที่ล็อกอินอยู่
3. **เพิ่มใน `auth.js`** — `getRole()`, `requireRole('admin'|'staff')`, และรองรับ `?next=` เพื่อพากลับหน้าเดิมหลังล็อกอิน
4. **`frontend/js/flow.js`** — เก็บ state ระหว่างขั้นตอนจอง (`item_id`, `product_id`, `timeslot_id`) ใน `sessionStorage` ก้อนเดียว แทนการส่ง query string ต่อกันไปเรื่อยๆ พร้อมฟังก์ชันเคลียร์เมื่อจองสำเร็จ
5. **เพิ่มฟังก์ชันใน `api.js`** ให้ครบตาม endpoint ใหม่ที่เพิ่มในข้อ 5
6. **Empty state + loading + error** ทุกหน้าที่ยิง API ต้องมี 3 สถานะนี้ ไม่ใช่หน้าขาวเปล่า
7. **Responsive** — หน้า staff ต้อง mobile-first, หน้า admin เน้น desktop, หน้าลูกค้าใช้ได้ทั้งคู่

---

## 7. Flow การใช้งานหลัก

```
ลูกค้าใหม่:
index → register → login → assessment-form → assessment-result
      → products → product-detail → select-datetime → checkout
      → booking-success → booking-status → booking-detail
      → (ช่างมารับของ / admin กด completed) → eco-dashboard → Share

ช่าง:
login → staff/jobs → staff/checklist → กด in_transit → กด completed

แอดมิน:
login → admin/index → admin/bookings (กดยืนยัน pending → confirmed)
                    → admin/timeslots (เปิดรอบใหม่ทุกสัปดาห์)
```

**จุดที่ต้องระวังในการเชื่อมหน้า**

- `POST /api/bookings` จะไม่ผ่านถ้า `item.status != "assessed"` → ก่อนพาไป products ต้องเช็คก่อนว่า item ยังว่างอยู่
- ยกเลิกการจองแล้ว item จะกลับเป็น `assessed` และ timeslot ว่างอีกครั้ง → หน้า my-items ต้อง refresh ให้ถูก
- 1 booking ผูก 1 item เท่านั้น ถ้าลูกค้ามีของเก่า 3 ชิ้นต้องจอง 3 ครั้ง → **ต้องสื่อสารให้ชัดในหน้า my-items** ไม่งั้นลูกค้างง

---

## 8. ลำดับการทำงาน (สั่ง Claude Code ทีละ Phase)

| Phase | ทำอะไร | ผลลัพธ์ |
|---|---|---|
| **0** | แยก `css/main.css` + `js/components.js` + `requireRole()` + `flow.js` แล้ว refactor 9 หน้าเดิมให้ใช้ของกลาง | โครงพร้อมขยาย ไม่มีหน้าใหม่ |
| **1** | Backend: upload รูป, role staff, booking detail, เปิดสิทธิ์ staff อัปเดตสถานะ | API พร้อม |
| **2** | เติมหน้าลูกค้าที่ขาด: assessment-result, my-items, product-detail, checkout, booking-success, booking-detail | Journey ลูกค้าครบวงจร |
| **3** | ปรับ 6 หน้าเดิม: landing, assessment-form, products, select-datetime, booking-status, eco-dashboard (+ ปุ่ม Share) | UX ตรงกับ Journey |
| **4** | หน้า staff 2 หน้า (mobile-first) | ปิด Journey ระยะ 4 |
| **5** | Backend CRUD products/timeslots + หน้า admin 6 หน้า | หลังบ้านครบ |
| **6** | เก็บงาน: 404, how-it-works, `disposal_destination` ใน eco-dashboard, ตรวจ responsive ทุกหน้า | ส่งงาน |

> ถ้าเวลาจำกัด ตัด Phase 6 และหน้า admin/products + admin/timeslots ได้ก่อน (ใช้ seed.py แทน)

---

## 9. เช็คลิสต์ก่อนส่งงาน

- [ ] ทุกหน้าที่ต้องล็อกอิน เรียก `requireLogin()` / `requireRole()` ตอนโหลด
- [ ] ทุกหน้าที่ยิง API มีสถานะ loading / empty / error ครบ
- [ ] ปุ่มที่ทำให้เกิดการเปลี่ยนแปลงถาวร (ลบ, ยกเลิกจอง) มี modal ยืนยัน
- [ ] error 409 ตอนจองซ้ำ handle แล้ว
- [ ] token หมดอายุ (401) เด้งกลับหน้า login อัตโนมัติทุกหน้า
- [ ] หน้า staff ใช้งานได้จริงบนจอมือถือ
- [ ] `BASE_URL` ใน api.js แก้ที่เดียวได้ ไม่มี hardcode localhost กระจายในหน้าอื่น
- [ ] อัปเดตโครงสร้างโปรเจกต์ใน README.MD ให้ตรงกับหน้าจริง
