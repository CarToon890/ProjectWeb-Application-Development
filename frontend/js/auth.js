// ============================================================
// auth.js — จัดการ token และสถานะล็อกอินฝั่ง client
// ต้องโหลด api.js ก่อนไฟล์นี้เสมอ (ใช้ฟังก์ชัน logout() จาก api.js)
// ============================================================

const TOKEN_KEY = "access_token"

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

function isLoggedIn() {
  return !!getToken()
}

// เรียกตอนโหลดหน้าที่ต้องล็อกอินก่อนใช้งาน — ถ้าไม่มี token ให้เด้งไปหน้า login
function requireLogin() {
  if (!isLoggedIn()) {
    location.href = "login.html"
  }
}

// ออกจากระบบ: แจ้ง backend แบบ best-effort แล้วลบ token ฝั่ง client เสมอ
async function handleLogout() {
  try {
    await logout()
  } catch (e) {
    // token อาจหมดอายุไปแล้ว ไม่เป็นไร ลบทิ้งฝั่ง client ต่อได้เลย
  }
  clearToken()
  location.href = "login.html"
}
