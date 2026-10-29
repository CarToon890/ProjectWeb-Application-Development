const { chromium } = require('playwright')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')

async function main() {
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) })
  const page = await browser.newPage()
  const user = { id: 7, username: 'qa', email: 'qa@example.test', full_name: 'QA', phone: '', address: '', role: 'user' }
  let updates = 0
  let assessment
  await page.addInitScript(() => localStorage.setItem('access_token', 'test-token'))
  await page.route('**/*', async route => {
    const url = new URL(route.request().url())
    if (url.hostname !== 'app.test') return route.abort()
    if (url.pathname === '/api/me') return route.fulfill({ json: user })
    if (url.pathname === '/api/items' && route.request().method() === 'POST') {
      assessment = route.request().postDataJSON()
      return route.fulfill({ json: { id: 1, estimated_price: 1500 } })
    }
    if (url.pathname === '/api/users/7' && route.request().method() === 'PUT') {
      Object.assign(user, route.request().postDataJSON())
      updates++
      return route.fulfill({ json: user })
    }
    const file = path.join(__dirname, '..', url.pathname)
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return route.fulfill({ status: 404, body: '' })
    return route.fulfill({ path: file, contentType: file.endsWith('.html') ? 'text/html' : file.endsWith('.css') ? 'text/css' : 'application/javascript' })
  })

  try {
    await page.goto('http://app.test/pages/profile.html')
    await page.waitForFunction(() => document.querySelector('#full_name').value === 'QA')
    await page.locator('#phone').fill('0812345678')
    await page.locator('#save-btn').click()
    await page.waitForTimeout(100)
    assert.equal(updates, 1, `profile save failed: ${await page.locator('#profile-error').textContent()}`)
    await page.reload()
    await page.waitForFunction(() => document.querySelector('#phone').value === '0812345678')

    await page.goto('http://app.test/pages/assessment-form.html')
    await page.locator('#submit-btn').click()
    assert.match(await page.locator('body').innerText(), /กรุณาเลือกประเภทเฟอร์นิเจอร์/)
    assert.equal(await page.locator('#condition-error').isVisible(), true)
    await page.locator('.type-btn').first().click()
    assert.equal(await page.locator('#type-error').isVisible(), false)
    await page.locator('#submit-btn').click()
    assert.match(await page.locator('body').innerText(), /กรุณาเลือกระดับสภาพสินค้า/)
    assert.equal(assessment, undefined)
    await page.locator('.condition-btn').first().click()
    assert.equal(await page.locator('#condition-error').isVisible(), false)
    await page.locator('#submit-btn').click()
    await page.waitForFunction(() => document.querySelector('#success-msg').style.display === 'flex')
    assert.equal(assessment.furniture_type, 'sofa')
    assert.equal(assessment.condition, 'good')
    console.log('Profile update persists and assessment explains missing selections')
  } finally {
    await browser.close()
  }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
