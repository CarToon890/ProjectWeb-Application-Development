// ============================================================
// api.js — ตัวกลางเรียก FastAPI ทุก endpoint
// แก้ BASE_URL เป็น deploy URL ตอน production
// ============================================================

const BASE_URL = "http://localhost:8000"

// ฟังก์ชันกลาง: เรียก API แล้วคืน JSON หรือ throw error
async function apiFetch(path, options = {}) {
  const res = await fetch(BASE_URL + path, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Error ${res.status}`)
  }
  return res.json()
}

// ส่งข้อมูลเฟอร์นิเจอร์ใหม่ → คืน item ที่สร้างแล้ว (มี id)
async function createItem(data) {
  return apiFetch("/api/items", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
}

// ดึง timeslot ที่ยังว่างอยู่ทั้งหมด
async function getTimeslots() {
  return apiFetch("/api/timeslots")
}

// จองนัด
async function createBooking(data) {
  return apiFetch("/api/bookings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
}

// ดึง eco stats สำหรับ dashboard
async function getEcoStats() {
  return apiFetch("/api/eco-stats")
}
