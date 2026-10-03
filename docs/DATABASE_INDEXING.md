# รายงานการเพิ่มประสิทธิภาพฐานข้อมูลด้วย Indexing (Database Indexing)

เอกสารสรุปการนำเทคนิค **Database Indexing** จากแบบฝึกหัด (`indexing-lab`) มาประยุกต์ใช้กับระบบจริงในโปรเจกต์ **Disposal Guilt / Upcycling Web Application** (FastAPI + PostgreSQL)

---

## 1. การวิเคราะห์จุดคอขวดของ Query ในระบบ (Query Analysis)

จากการตรวจสอบการทำงานของ Backend API พบว่ามี Query สำคัญที่ถูกเรียกใช้เป็นประจำ แต่เดิมไม่มี Index รองรับ ทำให้ฐานข้อมูลต้องทำงานแบบ **Sequential Scan (Seq Scan)** ซึ่งจะส่งผลให้ระบบช้าลงอย่างมากเมื่อมีข้อมูลการใช้งานเพิ่มขึ้น:

| จุดที่พบใน API | รูปแบบ Query ในโค้ด | ปัญหาเดิม (ไม่มี Index) |
|---|---|---|
| **หน้าประวัติการจองของผู้ใช้** (`GET /bookings`) | `SELECT * FROM booking WHERE user_id = :user_id` | ต้องสแกนทุกแถวเพื่อหารายการของ user คนเดียว (เหมือนตัวอย่าง Lab 01b) |
| **หน้าของเก่าที่ลงทะเบียน** (`GET /items`, `GET /eco-stats/me`) | `SELECT * FROM item WHERE user_id = :user_id` | ต้องสแกนทุกแถวในตาราง item |
| **หน้าเลือกรอบเวลานัดหมาย** (`GET /timeslots`) | `SELECT * FROM timeslot WHERE is_available = true AND datetime > NOW() ORDER BY datetime` | ต้องกรองสถานะ + กรองช่วงเวลา + เสียเวลาทำ **Quicksort** ทุกครั้งที่เรียก |
| **หน้าร้านค้า/แคตตาล็อกสินค้า** (`GET /products?category=...`) | `SELECT * FROM product WHERE category = :category` | ต้องสแกนทุกแถวเพื่อหาตามหมวดหมู่ |
| **งานของช่างและการดูรายละเอียดการจอง** (`GET /staff/jobs`) | `JOIN timeslot ON booking.timeslot_id = timeslot.id` | การเชื่อมตาราง Foreign Key ช้าลงเมื่อตารางมีขนาดใหญ่ |

---

## 2. การออกแบบและสร้าง Index (Index Design)

ยึดหลักการจาก **Lab 04, Lab 05, และ Lab 07**:
* **เลือกเฉพาะคอลัมน์ที่มี Cardinality เหมาะสม** และถูกเรียกใช้ในเงื่อนไข `WHERE` หรือ `JOIN` จริง
* **ไม่สร้าง Index พร่ำเพรื่อ** เพื่อลดพื้นที่ Disk และลดผลกระทบต่อความเร็วตอน `INSERT/UPDATE` (Lab 03 & 07)
* **ใช้ Composite Index ร่วมกับกฎ Leftmost Rule** สำหรับ Query ที่มีการกรองและจัดเรียงลำดับพร้อมกัน

### สรุป Index ที่เพิ่มเข้าไปในระบบ:

| ตาราง | ชื่อ Index | คอลัมน์ | ประเภท | วัตถุประสงค์ |
|---|---|---|---|---|
| `booking` | `ix_booking_user_id` | `user_id` | B-tree | เร่งความเร็วการดึงประวัติการจองของผู้ใช้แต่ละคน |
| `booking` | `ix_booking_item_id` | `item_id` | B-tree | เร่งความเร็วการดึงรายละเอียดของเก่าที่ผูกกับการจอง |
| `booking` | `ix_booking_timeslot_id` | `timeslot_id` | B-tree | เร่งความเร็วในการ JOIN ข้อมูลเวลานัดหมาย |
| `item` | `ix_item_user_id` | `user_id` | B-tree | เร่งความเร็วการค้นหาของเก่าของผู้ใช้ในระบบ |
| `item` | `ix_item_status` | `status` | B-tree | ใช้คำนวณสถิติ Eco Dashboard (`status = 'donated'`) |
| `product` | `ix_product_category` | `category` | B-tree | เร่งความเร็วการค้นหาสินค้าแยกตามหมวดหมู่ |
| `timeslot` | `ix_timeslot_available_datetime` | `(is_available, datetime)` | **Composite B-tree** | รองรับการกรองช่วงเวลาว่าง และข้ามขั้นตอน Sort (`ORDER BY datetime`) ตาม Leftmost Rule |

---

## 3. การอัปเดตไฟล์ในโปรเจกต์

1. **โมเดลฐานข้อมูล (`backend/app/models.py`):**
   * เพิ่ม `index=True` ให้กับ Foreign Key และคอลัมน์สืบค้น
   * เพิ่ม Composite Index `ix_timeslot_available_datetime` ใน `__table_args__` ของคลาส `Timeslot`
2. **ไฟล์ Alembic Migration (`backend/alembic/versions/0002_add_performance_indexes.py`):**
   * บันทึกการเปลี่ยนแปลง Schema เพื่อให้ Database บน Container หรือตอน Deploy ทำงานได้อัตโนมัติ

---

## 4. คำสั่ง SQL สำหรับทดสอบโดยตรง (DBeaver / pgAdmin / psql)

หากต้องการรันสร้าง Index บน Database โดยตรง:

```sql
-- 1. Index สำหรับตาราง Item
CREATE INDEX IF NOT EXISTS ix_item_user_id ON item (user_id);
CREATE INDEX IF NOT EXISTS ix_item_status ON item (status);

-- 2. Index สำหรับตาราง Product
CREATE INDEX IF NOT EXISTS ix_product_category ON product (category);

-- 3. Composite Index สำหรับ Timeslot (หัวใจสำคัญตาม Lab 05)
CREATE INDEX IF NOT EXISTS ix_timeslot_available_datetime ON timeslot (is_available, datetime);

-- 4. Index สำหรับตาราง Booking (Foreign Keys)
CREATE INDEX IF NOT EXISTS ix_booking_user_id ON booking (user_id);
CREATE INDEX IF NOT EXISTS ix_booking_item_id ON booking (item_id);
CREATE INDEX IF NOT EXISTS ix_booking_timeslot_id ON booking (timeslot_id);
```

---

## 5. การทดสอบและเปรียบเทียบผลลัพธ์ (Verification ด้วย EXPLAIN ANALYZE)

### เคสที่ 1: การค้นหารอบเวลาว่าง (`Timeslot`)

```sql
EXPLAIN ANALYZE
SELECT * FROM timeslot
WHERE is_available = true AND datetime > NOW()
ORDER BY datetime;
```

* **ก่อนมี Index:**
  * Plan: `Seq Scan on timeslot` + `Sort: Sort Method: quicksort`
  * สาเหตุ: Database ต้องอ่านข้อมูลทั้งหมดในตารางและนำมากรอง จากนั้นต้องส่งต่อให้ CPU ทำการ Sort เรียงวันที่
* **หลังมี Index (`ix_timeslot_available_datetime`):**
  * Plan: `Index Scan using ix_timeslot_available_datetime on timeslot`
  * ผลลัพธ์: **ไม่มีขั้นตอน Sort เกิดขึ้น** เพราะ B-Tree จัดเรียงตามลำดับ `(is_available, datetime)` ให้อยู่แล้ว ข้อมูลถูกดึงตามลำดับของ Index ทันที

### เคสที่ 2: การค้นหาการจองตามผู้ใช้ (`Booking`)

```sql
EXPLAIN ANALYZE
SELECT * FROM booking WHERE user_id = 1;
```

* **ก่อนมี Index:** `Seq Scan on booking (Filter: user_id = 1)`
* **หลังมี Index:** `Bitmap Index Scan on ix_booking_user_id` / `Index Scan` ดึงเฉพาะแถวของลูกค้ารายนั้นได้ทันที
