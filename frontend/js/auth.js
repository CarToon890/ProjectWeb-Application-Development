// ============================================================
// auth.js — จัดการ token และสถานะล็อกอินฝั่ง client
// ต้องโหลด api.js ก่อนไฟล์นี้เสมอ (ใช้ฟังก์ชัน logout() จาก api.js)
// ============================================================

const TOKEN_KEY = "access_token"
const ROLE_KEY = "user_role"

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ROLE_KEY)
}

function isLoggedIn() {
  return !!getToken()
}

// role ไม่ได้อยู่ใน JWT (มีแค่ user id) ต้องเรียก getMe() แล้ว cache ไว้เอง
function cacheRole(role) {
  localStorage.setItem(ROLE_KEY, role)
}

function getRole() {
  return localStorage.getItem(ROLE_KEY)
}

// path ไป login.html เทียบจากหน้าปัจจุบัน — ใช้ได้ทั้งจาก pages/ และ staff/ admin/ (ลึกเท่ากันจาก frontend root)
function loginPath() {
  return location.pathname.includes("/pages/") ? "login.html" : "../pages/login.html"
}

// เรียกตอนโหลดหน้าที่ต้องล็อกอินก่อนใช้งาน — ถ้าไม่มี token ให้เด้งไปหน้า login
// พ่วง ?next= เพื่อพากลับหน้าเดิมหลังล็อกอินสำเร็จ
// login.html คำนวณปลายทางเทียบจากตัวเองเสมอ (อยู่ใน pages/) — ถ้าหน้าปัจจุบันไม่ได้อยู่ pages/
// (เช่น staff/ admin/) ต้องใส่ชื่อโฟลเดอร์นำหน้าไปด้วย ไม่งั้น login.html จะหาไฟล์ผิดที่
function requireLogin() {
  if (!isLoggedIn()) {
    const segments = location.pathname.split("/").filter(Boolean)
    const filename = segments[segments.length - 1] || "index.html"
    const dir = segments.length >= 2 ? segments[segments.length - 2] : ""
    const nextPath = dir === "pages" ? filename : `../${dir ? dir + "/" : ""}${filename}`
    const next = encodeURIComponent(nextPath + location.search)
    location.href = `${loginPath()}?next=${next}`
  }
}

// เรียกตอนโหลดหน้าที่ต้องมี role ตรงตามที่กำหนดเท่านั้น (เช่น 'admin', 'staff' หรือ ['staff','admin'])
// ถ้ายังไม่ล็อกอิน → เด้งไป login | ล็อกอินแล้วแต่ role ไม่ตรง → เด้งกลับหน้าแรก
async function requireRole(role) {
  requireLogin()
  if (!isLoggedIn()) return

  const allowedRoles = Array.isArray(role) ? role : [role]

  let currentRole = getRole()
  if (!currentRole) {
    try {
      const me = await getMe()
      currentRole = me.role
      cacheRole(currentRole)
    } catch (e) {
      // token หมดอายุหรือเรียกไม่ได้ — ถือว่ายืนยันตัวตนไม่ผ่าน
      await handleLogout()
      return
    }
  }

  if (!allowedRoles.includes(currentRole)) {
    location.href = "../index.html"
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
  location.href = loginPath()
}
