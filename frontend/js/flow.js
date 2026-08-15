// ============================================================
// flow.js — เก็บ state ระหว่างขั้นตอนจอง (item_id, product_id, timeslot_id)
// เก็บใน sessionStorage ก้อนเดียวแทนการส่งต่อกันผ่าน query string ยาวๆ
// ============================================================

const FLOW_KEY = "booking_flow"

function getFlow() {
  try {
    return JSON.parse(sessionStorage.getItem(FLOW_KEY)) || {}
  } catch (e) {
    return {}
  }
}

function setFlow(partial) {
  sessionStorage.setItem(FLOW_KEY, JSON.stringify({ ...getFlow(), ...partial }))
}

function clearFlow() {
  sessionStorage.removeItem(FLOW_KEY)
}
