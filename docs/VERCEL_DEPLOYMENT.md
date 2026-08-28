# คู่มือการ Deploy โปรเจกต์ขึ้น Vercel + Supabase

คู่มือนี้จะแนะนำขั้นตอนการนำโปรเจกต์ **The Disposal Guilt** ขึ้นใช้งานบน **Vercel** แบบ Fullstack (Static Frontend + FastAPI Serverless) ร่วมกับฐานข้อมูลและที่เก็บไฟล์ของ **Supabase**

---

## สรุปภาพรวมสิ่งที่ต้องเตรียม
1. บัญชี **GitHub** สำหรับเก็บ Repository
2. บัญชี **Supabase** (ฟรี) สำหรับ PostgreSQL Database และ Storage Bucket
3. บัญชี **Vercel** (ฟรี) สำหรับ Deploy เว็บไซต์และ Serverless API

---

## ขั้นตอนที่ 1: ตั้งค่า Supabase (Database & Storage)

### 1.1 สร้าง Project บน Supabase
1. เข้าไปที่ [supabase.com](https://supabase.com) และเข้าสู่ระบบ
2. กด **New Project**
3. ตั้งชื่อโปรเจกต์ (เช่น `disposal-guilt`) และตั้งรหัสผ่าน **Database Password** (จดรหัสผ่านนี้ไว้ให้ดี)
4. เลือก Region ใกล้ไทย เช่น `Singapore (ap-southeast-1)`
5. รอ 1-2 นาทีจนกว่าระบบจะสร้างฐานข้อมูลเสร็จ

### 1.2 เอาค่า Connection String (DATABASE_URL)
1. ไปที่เมนู **Project Settings** (รูปเฟือง) -> **Database**
2. เลื่อนลงมาที่หัวข้อ **Connection string**
3. เลือกแท็บ **URI** หรือ **Connection Pooling (Session Mode)**
4. ตัวอย่าง URL:
   ```
   postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
   *(อย่าลืมแทนที่ `[YOUR-PASSWORD]` ด้วยรหัสผ่านจริงที่ตั้งไว้ในข้อ 1.1)*

### 1.3 สร้าง Storage Bucket สำหรับรูปภาพ
1. ไปที่เมนู **Storage** ในแท็บด้านซ้าย
2. กด **New bucket**
3. ตั้งชื่อ Bucket ว่า `uploads`
4. **สำคัญมาก**: ติ๊กเปิด **Public bucket** (เพื่อให้บุคคลทั่วไปสามารถดูรูปภาพผ่านลิงก์ได้)
5. กด **Save**

### 1.4 เอาค่า Supabase URL และ Key
1. ไปที่เมนู **Project Settings** -> **API**
2. คัดลอกค่า:
   - **Project URL** (เช่น `https://abcdefghijklmnop.supabase.co`)
   - **anon / public key** หรือ **service_role key** (แนะนำให้ใช้ service_role key สำหรับ backend upload)

---

## ขั้นตอนที่ 2: เตรียมโค้ดและ Push ขึ้น GitHub
1. เปิด Terminal ในเครื่องของคุณ
2. เพิ่มไฟล์ทั้งหมดและ Commit:
   ```bash
   git add .
   git commit -m "feat: configure vercel serverless and supabase support"
   git push origin main
   ```

---

## ขั้นตอนที่ 3: Deploy ขึ้น Vercel

1. เข้าไปที่ [vercel.com](https://vercel.com) และเข้าสู่ระบบด้วย GitHub
2. กดปุ่ม **Add New...** -> **Project**
3. เลือก Repository `ProjectWeb-Application-Development` แล้วกด **Import**
4. ในหน้า **Configure Project**:
   - **Framework Preset**: เลือก `Other`
   - **Root Directory**: ปล่อยว่างไว้เป็น `./`
5. เลื่อนลงมาที่หัวข้อ **Environment Variables** แล้วเพิ่มตัวแปรดังนี้:

| Key | Value ตัวอย่าง | คำอธิบาย |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres.xxx:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres` | ลิงก์เชื่อมต่อฐานข้อมูล Supabase |
| `JWT_SECRET_KEY` | `your-secret-random-key-here-minimum-32-chars` | คีย์สำหรับเข้ารหัส JWT Token |
| `JWT_ALGORITHM` | `HS256` | อัลกอริทึมเข้ารหัส |
| `JWT_EXPIRE_MINUTES` | `1440` | อายุ Token (นาที) |
| `SUPABASE_URL` | `https://your-project.supabase.co` | URL ของ Supabase Project |
| `SUPABASE_KEY` | `eyJhbGciOi...` | Supabase API Key (service_role หรือ anon) |
| `SUPABASE_BUCKET` | `uploads` | ชื่อ Bucket ที่สร้างไว้ |

6. กดปุ่ม **Deploy**
7. รอ Vercel ทำการ Build และ Deploy ประมาณ 1-2 นาที เมื่อเสร็จจะได้ Domain URL สำหรับเข้าใช้งาน (เช่น `https://project-web-xxx.vercel.app`)

---

## ขั้นตอนที่ 4: ตรวจสอบการทำงานหลัง Deploy

1. เข้าไปยัง URL ของ Vercel
2. ทดสอบหน้าแรก (`index.html`) และหน้าสินค้า (`/pages/products.html`)
3. ทดสอบการสมัครสมาชิก (`/pages/register.html`) และเข้าสู่ระบบ (`/pages/login.html`)
4. บัญชีเริ่มต้นที่ระบบสร้างให้ (Seed Data):
   - **Admin**: Username: `admin` / Password: `admin1234`
   - **Staff**: Username: `staff` / Password: `staff1234`
5. ทดสอบเข้าสู่หน้าแอดมิน (`/admin/index.html`) หรือเจ้าหน้าที่ (`/staff/jobs.html`)
6. ทดสอบการอัปโหลดรูปภาพในการประเมินเฟอร์นิเจอร์ หรือหน้าจัดการสินค้า

---

## การแก้ไขปัญหาที่พบบ่อย (Troubleshooting)

### 1. Database Connection Timeout / SSL Error
- ตรวจสอบว่า `DATABASE_URL` ใช้พอร์ต connection pooler (เช่น `6543` หรือ `5432`) และไม่มีอักขระพิเศษในรหัสผ่านที่ไม่ได้ผ่าน URL encoding (เช่น `@`, `#`, `%`)
- ตรวจสอบว่าใน `DATABASE_URL` ขึ้นต้นด้วย `postgresql://`

### 2. Upload รูปภาพแล้วขึ้น Error 500
- ตรวจสอบว่าได้สร้าง Storage Bucket ชื่อ `uploads` และเปิดเป็น **Public** แล้วหรือยัง
- ตรวจสอบว่าได้ใส่ `SUPABASE_URL` และ `SUPABASE_KEY` ใน Vercel Environment Variables ถูกต้องหรือไม่

### 3. API Return 404
- ตรวจสอบว่ามีไฟล์ `vercel.json` และโฟลเดอร์ `api/index.py` อยู่ที่ root ของโปรเจกต์บน GitHub หรือไม่
