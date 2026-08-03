// ============================================================
// api.js — ตัวกลางเรียก FastAPI ทุก endpoint
// แก้ BASE_URL เป็น deploy URL ตอน production
// token เก็บใน localStorage คีย์ "access_token" (auth.js จะเป็นคนจัดการ)
// ============================================================

const BASE_URL = "http://localhost:8000"

// ฟังก์ชันกลาง: เรียก API แล้วคืน JSON หรือ throw error
// แนบ Authorization: Bearer <token> อัตโนมัติถ้ามี token ใน localStorage
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token")
  const headers = { ...(options.headers || {}) }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const res = await fetch(BASE_URL + path, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Error ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

// ฟังก์ชันช่วยส่ง JSON body (ใส่ Content-Type ให้อัตโนมัติ)
function jsonBody(method, data) {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }
}

// ---------- Auth ----------
async function register(data) {
  return apiFetch("/api/register", jsonBody("POST", data))
}

async function login(username, password) {
  return apiFetch("/api/login", jsonBody("POST", { username, password }))
}

async function logout() {
  return apiFetch("/api/logout", { method: "POST" })
}

async function changePassword(oldPassword, newPassword) {
  return apiFetch("/api/change-password", jsonBody("POST", { old_password: oldPassword, new_password: newPassword }))
}

async function checkUsername(name) {
  return apiFetch(`/api/check-username/${encodeURIComponent(name)}`)
}

// ---------- Users ----------
async function getMe() {
  return apiFetch("/api/me")
}

async function getUsers(page = 1, limit = 10) {
  return apiFetch(`/api/users?page=${page}&limit=${limit}`)
}

async function getUser(id) {
  return apiFetch(`/api/users/${id}`)
}

async function updateUser(id, data) {
  return apiFetch(`/api/users/${id}`, jsonBody("PUT", data))
}

async function deleteUser(id) {
  return apiFetch(`/api/users/${id}`, { method: "DELETE" })
}

// ---------- Items ----------
async function createItem(data) {
  return apiFetch("/api/items", jsonBody("POST", data))
}

async function getItems() {
  return apiFetch("/api/items")
}

async function getItem(id) {
  return apiFetch(`/api/items/${id}`)
}

async function updateItem(id, data) {
  return apiFetch(`/api/items/${id}`, jsonBody("PUT", data))
}

async function deleteItem(id) {
  return apiFetch(`/api/items/${id}`, { method: "DELETE" })
}

// ---------- Products ----------
async function getProducts(category) {
  const query = category ? `?category=${encodeURIComponent(category)}` : ""
  return apiFetch(`/api/products${query}`)
}

async function getProduct(id) {
  return apiFetch(`/api/products/${id}`)
}

// ---------- Bookings ----------
async function getTimeslots() {
  return apiFetch("/api/timeslots")
}

async function createBooking(data) {
  return apiFetch("/api/bookings", jsonBody("POST", data))
}

async function getBookings() {
  return apiFetch("/api/bookings")
}

async function getBooking(id) {
  return apiFetch(`/api/bookings/${id}`)
}

async function cancelBooking(id) {
  return apiFetch(`/api/bookings/${id}/cancel`, { method: "PUT" })
}

async function updateBookingStatus(id, status) {
  return apiFetch(`/api/bookings/${id}/status`, jsonBody("PUT", { status }))
}

// ---------- Eco ----------
async function getEcoStats() {
  return apiFetch("/api/eco-stats")
}

async function getEcoStatsMe() {
  return apiFetch("/api/eco-stats/me")
}
