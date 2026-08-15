// ============================================================
// components.js — UI กลาง: renderNav / renderFooter / toast
// ต้องโหลด api.js + auth.js ก่อนไฟล์นี้เสมอ (ใช้ isLoggedIn, handleLogout)
// ============================================================

const CUSTOMER_NAV_LINKS = [
  { key: "home", label: "หน้าแรก", path: "index.html" },
  { key: "assess", label: "ประเมินของเก่า", path: "pages/assessment-form.html" },
  { key: "myitems", label: "ของเก่าของฉัน", path: "pages/my-items.html" },
  { key: "bookings", label: "การจองของฉัน", path: "pages/booking-status.html" },
  { key: "eco", label: "Eco Dashboard", path: "pages/eco-dashboard.html" },
  { key: "profile", label: "โปรไฟล์", path: "pages/profile.html" },
]

const STAFF_NAV_LINKS = [{ key: "jobs", label: "งานของฉัน", path: "staff/jobs.html" }]

const ADMIN_NAV_LINKS = [
  { key: "dashboard", label: "Dashboard", path: "admin/index.html" },
  { key: "a-bookings", label: "การจอง", path: "admin/bookings.html" },
  { key: "a-items", label: "ของเก่า", path: "admin/items.html" },
  { key: "a-products", label: "สินค้า", path: "admin/products.html" },
  { key: "a-timeslots", label: "รอบเวลา", path: "admin/timeslots.html" },
  { key: "a-users", label: "ผู้ใช้", path: "admin/users.html" },
]

// path กำหนดเทียบจาก frontend root เสมอ (เช่น "pages/profile.html")
// root คือ prefix ของหน้าปัจจุบันเทียบจาก frontend root ("" ที่ root, "../" ที่ลึกลงไป 1 ชั้น)
// dir คือชื่อโฟลเดอร์ของหน้าปัจจุบัน ("pages" | "staff" | "admin") ใช้แยกว่าลิงก์อยู่โฟลเดอร์เดียวกันไหม
// ค่า default ของ dir เป็น "pages" เพื่อคงพฤติกรรมเดิมของหน้าที่เรียกแบบไม่ระบุ dir (ทุกหน้าที่มีอยู่ก่อนอยู่ใน pages/)
function resolveNavHref(path, root, dir = "pages") {
  if (root === "") return path
  const slashIdx = path.indexOf("/")
  const pathDir = slashIdx === -1 ? "" : path.slice(0, slashIdx)
  if (pathDir === dir) return path.slice(dir.length + 1)
  return root + path
}

// วาง <div id="app-nav"></div> ไว้บนสุดของ body แล้วเรียกฟังก์ชันนี้
// options: { root: "" | "../", dir: "pages"|"staff"|"admin", active: string }
function renderNav({ root = "", dir = "pages", active = "" } = {}) {
  const mount = document.getElementById("app-nav")
  if (!mount) return

  const loggedIn = isLoggedIn()
  const role = getRole()
  const navLinks = role === "admin" ? ADMIN_NAV_LINKS : role === "staff" ? STAFF_NAV_LINKS : CUSTOMER_NAV_LINKS

  const linksHtml = loggedIn
    ? navLinks.map(
        (l) =>
          `<a href="${resolveNavHref(l.path, root, dir)}" class="${l.key === active ? "active" : ""}">${l.label}</a>`
      ).join("") + `<button class="logout-btn" id="nav-logout-btn">ออกจากระบบ</button>`
    : `<a href="${resolveNavHref("pages/login.html", root, dir)}">เข้าสู่ระบบ</a>` +
      `<a href="${resolveNavHref("pages/register.html", root, dir)}">สมัครสมาชิก</a>`

  mount.classList.add("nav")
  mount.innerHTML = `
    <div class="logo">THE DISPOSAL GUILT</div>
    <div class="links">${linksHtml}</div>
  `

  const logoutBtn = document.getElementById("nav-logout-btn")
  if (logoutBtn) logoutBtn.addEventListener("click", handleLogout)
}

// วาง <div id="app-footer"></div> ไว้ล่างสุดของ body แล้วเรียกฟังก์ชันนี้ (ใช้ตอนต้องการ)
function renderFooter() {
  const mount = document.getElementById("app-footer")
  if (!mount) return
  mount.innerHTML = `<div class="footer-text">© ${new Date().getFullYear()} The Disposal Guilt</div>`
}

// แจ้งเตือนแบบลอย ไม่บล็อกหน้าจอ — ใช้แทน alert()
// type: "info" | "success" | "error"
function toast(message, type = "info", duration = 3000) {
  let stack = document.getElementById("toast-stack")
  if (!stack) {
    stack = document.createElement("div")
    stack.id = "toast-stack"
    document.body.appendChild(stack)
  }
  const el = document.createElement("div")
  el.className = `toast toast-${type}`
  el.textContent = message
  stack.appendChild(el)
  setTimeout(() => el.remove(), duration)
}

// modal ยืนยันก่อนทำสิ่งที่ย้อนกลับไม่ได้ (ยกเลิกจอง, ลบรายการ) — ใช้แทน confirm()
// คืนค่า Promise<boolean> — true ถ้ากดยืนยัน
function confirmDialog(message, { confirmLabel = "ยืนยัน", cancelLabel = "ยกเลิก" } = {}) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div")
    overlay.className = "modal-overlay"
    overlay.innerHTML = `
      <div class="modal-box">
        <p class="modal-message">${message}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" id="modal-cancel-btn">${cancelLabel}</button>
          <button class="btn btn-danger" id="modal-confirm-btn">${confirmLabel}</button>
        </div>
      </div>
    `
    document.body.appendChild(overlay)

    const close = (result) => {
      overlay.remove()
      resolve(result)
    }

    overlay.querySelector("#modal-cancel-btn").addEventListener("click", () => close(false))
    overlay.querySelector("#modal-confirm-btn").addEventListener("click", () => close(true))
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) close(false)
    })
  })
}
