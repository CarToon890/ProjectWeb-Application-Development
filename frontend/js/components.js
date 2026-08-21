// ============================================================
// components.js — UI กลาง v3.0 (Professional Edition)
// Navbar + Icons · Stepper Wizard · Rich Footer · Dark Mode
// Toast + Progress · Breadcrumb · Ripple · Scroll Animations
// ============================================================

// ---------- Nav Link Definitions (with Lucide icon names) ----------
const CUSTOMER_NAV_LINKS = [
  { key: "home", label: "หน้าแรก", icon: "home", path: "index.html" },
  { key: "assess", label: "ประเมินของเก่า", icon: "clipboard-list", path: "pages/assessment-form.html" },
  { key: "myitems", label: "ของเก่าของฉัน", icon: "archive", path: "pages/my-items.html" },
  { key: "products", label: "แคตตาล็อกสินค้า", icon: "shopping-bag", path: "pages/products.html" },
  { key: "bookings", label: "การจองของฉัน", icon: "calendar-check", path: "pages/booking-status.html" },
  { key: "eco", label: "Eco Dashboard", icon: "leaf", path: "pages/eco-dashboard.html" },
  { key: "profile", label: "โปรไฟล์", icon: "user", path: "pages/profile.html" },
]

const STAFF_NAV_LINKS = [
  { key: "jobs", label: "งานของฉัน", icon: "briefcase", path: "staff/jobs.html" },
  { key: "profile", label: "โปรไฟล์", icon: "user", path: "pages/profile.html" },
]

const ADMIN_NAV_LINKS = [
  { key: "dashboard", label: "Dashboard", icon: "layout-dashboard", path: "admin/index.html" },
  { key: "a-bookings", label: "การจอง", icon: "calendar-check", path: "admin/bookings.html" },
  { key: "a-items", label: "ของเก่า", icon: "archive", path: "admin/items.html" },
  { key: "a-products", label: "สินค้า", icon: "package", path: "admin/products.html" },
  { key: "a-timeslots", label: "รอบเวลา", icon: "clock", path: "admin/timeslots.html" },
  { key: "a-users", label: "ผู้ใช้", icon: "users", path: "admin/users.html" },
]

// ---------- Path Resolution ----------
function resolveNavHref(path, root, dir = "pages") {
  if (root === "") return path
  const slashIdx = path.indexOf("/")
  const pathDir = slashIdx === -1 ? "" : path.slice(0, slashIdx)
  if (pathDir === dir) return path.slice(dir.length + 1)
  return root + path
}

// ---------- Render Nav ----------
function renderNav({ root = "", dir = "pages", active = "" } = {}) {
  const mount = document.getElementById("app-nav")
  if (!mount) return

  const loggedIn = isLoggedIn()
  const role = getRole()
  const navLinks = role === "admin" ? ADMIN_NAV_LINKS
                  : role === "staff" ? STAFF_NAV_LINKS
                  : CUSTOMER_NAV_LINKS

  let linksHtml
  if (loggedIn) {
    linksHtml = navLinks.map(l =>
      `<a href="${resolveNavHref(l.path, root, dir)}" class="nav-link ${l.key === active ? "active" : ""}">
        <i data-lucide="${l.icon}"></i><span>${l.label}</span>
      </a>`
    ).join("") +
    `<button class="nav-link logout-btn" id="nav-logout-btn">
      <i data-lucide="log-out"></i><span>ออกจากระบบ</span>
    </button>`
  } else {
    linksHtml =
      `<a href="${resolveNavHref("pages/products.html", root, dir)}" class="nav-link">
        <i data-lucide="shopping-bag"></i><span>สินค้าใหม่</span>
      </a>` +
      `<a href="${resolveNavHref("pages/login.html", root, dir)}" class="nav-link">
        <i data-lucide="log-in"></i><span>เข้าสู่ระบบ</span>
      </a>` +
      `<a href="${resolveNavHref("pages/register.html", root, dir)}" class="nav-link">
        <i data-lucide="user-plus"></i><span>สมัครสมาชิก</span>
      </a>`
  }

  mount.className = "nav"
  mount.innerHTML = `
    <a href="${resolveNavHref("index.html", root, dir)}" class="nav-brand">
      <i data-lucide="recycle"></i>THE DISPOSAL GUILT
    </a>
    <div class="nav-links" id="nav-links">${linksHtml}</div>
    <div class="nav-actions">
      <button class="theme-toggle" id="theme-toggle" title="สลับธีม">
        <i data-lucide="sun" class="theme-icon-light"></i>
        <i data-lucide="moon" class="theme-icon-dark"></i>
      </button>
      <button class="nav-hamburger" id="nav-toggle" aria-label="เปิดเมนู">
        <i data-lucide="menu"></i>
      </button>
    </div>
    <div class="nav-overlay" id="nav-overlay"></div>
  `

  // Event handlers
  const logoutBtn = document.getElementById("nav-logout-btn")
  if (logoutBtn) logoutBtn.addEventListener("click", handleLogout)

  const themeBtn = document.getElementById("theme-toggle")
  if (themeBtn) themeBtn.addEventListener("click", toggleTheme)

  const toggleBtn = document.getElementById("nav-toggle")
  const navLinksEl = document.getElementById("nav-links")
  const overlay = document.getElementById("nav-overlay")

  if (toggleBtn && navLinksEl && overlay) {
    const closeDrawer = () => {
      navLinksEl.classList.remove("open")
      overlay.classList.remove("open")
    }
    toggleBtn.addEventListener("click", () => {
      navLinksEl.classList.toggle("open")
      overlay.classList.toggle("open")
    })
    overlay.addEventListener("click", closeDrawer)
    navLinksEl.querySelectorAll(".nav-link").forEach(link => {
      link.addEventListener("click", closeDrawer)
    })
  }

  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })
}

// ---------- Stepper Wizard Component ----------
const TRADE_IN_STEPS = [
  { step: 1, title: "ประเมินของเก่า", desc: "ถ่ายรูป & เลือกสภาพ", icon: "camera" },
  { step: 2, title: "เลือกของใหม่", desc: "รับส่วนลด Trade-in", icon: "shopping-bag" },
  { step: 3, title: "นัดหมายวันเวลา", desc: "รอบรับของ & ส่งของ", icon: "calendar" },
  { step: 4, title: "ยืนยันการจอง", desc: "สรุปยอด & ที่อยู่", icon: "check-circle" },
]

function renderStepper(currentStep = 1, mountId = "app-stepper") {
  const mount = document.getElementById(mountId)
  if (!mount) return

  let html = `<div class="stepper-wrap"><div class="stepper">`
  
  TRADE_IN_STEPS.forEach((s, idx) => {
    const isCompleted = s.step < currentStep
    const isActive = s.step === currentStep
    const stateClass = isCompleted ? "completed" : isActive ? "active" : ""
    
    html += `
      <div class="stepper-step ${stateClass}">
        <div class="stepper-circle">
          ${isCompleted ? '<i data-lucide="check"></i>' : `<i data-lucide="${s.icon}"></i>`}
        </div>
        <div class="stepper-info">
          <span class="stepper-title">${s.step}. ${s.title}</span>
          <span class="stepper-desc">${s.desc}</span>
        </div>
      </div>
    `
    
    if (idx < TRADE_IN_STEPS.length - 1) {
      const dividerCompleted = s.step < currentStep ? "completed" : ""
      html += `<div class="stepper-divider ${dividerCompleted}"></div>`
    }
  })

  html += `</div></div>`
  mount.innerHTML = html

  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })
}

// ---------- Breadcrumb Component ----------
function renderBreadcrumbs(items = [], mountId = "app-breadcrumb") {
  const mount = document.getElementById(mountId)
  if (!mount || !items.length) return

  let html = `<div class="breadcrumb">`
  items.forEach((item, idx) => {
    if (idx > 0) html += `<i data-lucide="chevron-right"></i>`
    if (item.url && idx < items.length - 1) {
      html += `<a href="${item.url}">${item.label}</a>`
    } else {
      html += `<span class="breadcrumb-current">${item.label}</span>`
    }
  })
  html += `</div>`
  mount.innerHTML = html

  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })
}

// ---------- Rich Footer (4 Columns) ----------
function renderFooter({ root = "", dir = "pages" } = {}) {
  const mount = document.getElementById("app-footer")
  if (!mount) return

  mount.className = "rich-footer"
  mount.innerHTML = `
    <div class="container-xl">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="nav-brand" style="margin-bottom: 12px; font-size: 16px;">
            <i data-lucide="recycle" style="color: var(--ok);"></i>THE DISPOSAL GUILT
          </div>
          <p style="font-size: 13px; color: var(--muted); line-height: 1.6; margin-bottom: 16px;">
            แพลตฟอร์ม Trade-in เฟอร์นิเจอร์: "ทิ้งก็เสียดาย ขายก็ลำบาก" รับจบในรอบเดียว ส่งของใหม่พร้อมรับของเก่า ช่วยลดขยะและคาร์บอนสู่โลก
          </p>
          <div style="display: flex; gap: 8px;">
            <span class="badge badge-ok"><i data-lucide="leaf"></i> Green Tech Platform</span>
          </div>
        </div>

        <div class="footer-col">
          <h4>บริการสำหรับลูกค้า</h4>
          <ul class="footer-links">
            <li><a href="${resolveNavHref("pages/assessment-form.html", root, dir)}"><i data-lucide="camera"></i> ประเมินราคาของเก่า</a></li>
            <li><a href="${resolveNavHref("pages/products.html", root, dir)}"><i data-lucide="shopping-bag"></i> แคตตาล็อกของใหม่</a></li>
            <li><a href="${resolveNavHref("pages/booking-status.html", root, dir)}"><i data-lucide="calendar"></i> ตรวจสอบสถานะการจอง</a></li>
            <li><a href="${resolveNavHref("pages/eco-dashboard.html", root, dir)}"><i data-lucide="leaf"></i> สถิติสิ่งแวดล้อม (Eco)</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>ลิงก์ด่วน</h4>
          <ul class="footer-links">
            <li><a href="${resolveNavHref("pages/my-items.html", root, dir)}"><i data-lucide="archive"></i> ของเก่าของฉัน</a></li>
            <li><a href="${resolveNavHref("pages/profile.html", root, dir)}"><i data-lucide="user"></i> ข้อมูลส่วนตัว</a></li>
            <li><a href="${resolveNavHref("pages/login.html", root, dir)}"><i data-lucide="log-in"></i> เข้าสู่ระบบ</a></li>
            <li><a href="${resolveNavHref("pages/register.html", root, dir)}"><i data-lucide="user-plus"></i> สมัครสมาชิก</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>เป้าหมายความยั่งยืน</h4>
          <p style="font-size: 13px; color: var(--muted); line-height: 1.6; margin-bottom: 12px;">
            ทุกการ Trade-in ช่วยลดการตัดไม้ทำลายป่า และลดการปล่อยก๊าซเรือนกระจกจากการกำจัดขยะขนาดใหญ่
          </p>
          <div style="background: var(--surface-2); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border); font-size: 12px; color: var(--muted);">
            🌱 1 ชิ้นเฟอร์นิเจอร์ $\approx$ ลด CO₂ ได้ ~12-36 กก.
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <div>© ${new Date().getFullYear()} The Disposal Guilt — โครงการพัฒนาระบบเว็บแอปพลิเคชัน</div>
        <div style="display: flex; gap: 16px;">
          <span>HTML5 · CSS3 · Vanilla JS · FastAPI · PostgreSQL</span>
        </div>
      </div>
    </div>
  `

  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })
}

// ---------- Toast (with icon + progress bar) ----------
const TOAST_ICONS = {
  info: "info",
  success: "check-circle",
  error: "alert-circle",
}

function toast(message, type = "info", duration = 3000) {
  let stack = document.getElementById("toast-stack")
  if (!stack) {
    stack = document.createElement("div")
    stack.id = "toast-stack"
    document.body.appendChild(stack)
  }
  const iconName = TOAST_ICONS[type] || "info"
  const el = document.createElement("div")
  el.className = `toast toast-${type}`
  el.style.setProperty("--toast-duration", `${duration}ms`)
  el.innerHTML = `<i data-lucide="${iconName}"></i><span class="toast-text">${message}</span>`
  stack.appendChild(el)

  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })

  setTimeout(() => {
    el.style.animation = "toast-slide-out 0.3s ease-in forwards"
    setTimeout(() => el.remove(), 300)
  }, duration)
}

// ---------- Confirm Dialog ----------
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

// ---------- Dark Mode ----------
function initTheme() {
  const saved = localStorage.getItem("theme")
  if (saved) {
    document.documentElement.setAttribute("data-theme", saved)
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.setAttribute("data-theme", "dark")
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme")
  const next = current === "dark" ? "light" : "dark"
  document.documentElement.setAttribute("data-theme", next)
  localStorage.setItem("theme", next)
  if (typeof lucide !== "undefined") lucide.createIcons({ nameAttr: "data-lucide" })
}

// ---------- Scroll Animations ----------
function initScrollAnimations() {
  const elements = document.querySelectorAll(".animate-on-scroll")
  if (!elements.length) return

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible")
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" })

  elements.forEach(el => observer.observe(el))
}

// ---------- Button Ripple ----------
function initRipple() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn")
    if (!btn || btn.disabled) return

    const existing = btn.querySelector(".ripple")
    if (existing) existing.remove()

    const ripple = document.createElement("span")
    ripple.className = "ripple"

    const rect = btn.getBoundingClientRect()
    const size = Math.max(rect.width, rect.height) * 2
    ripple.style.width = ripple.style.height = size + "px"
    ripple.style.left = (e.clientX - rect.left - size / 2) + "px"
    ripple.style.top = (e.clientY - rect.top - size / 2) + "px"

    btn.appendChild(ripple)
    setTimeout(() => ripple.remove(), 600)
  })
}

// ---------- Init Page ----------
function initPage() {
  initTheme()
  initScrollAnimations()
  initRipple()
  if (typeof lucide !== "undefined") {
    lucide.createIcons({ nameAttr: "data-lucide" })
  }
}

initTheme()
