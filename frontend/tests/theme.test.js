const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')

const root = path.resolve(__dirname, '..')
const directories = ['', 'pages', 'admin', 'staff']
for (const directory of directories) {
  for (const file of fs.readdirSync(path.join(root, directory)).filter(name => name.endsWith('.html'))) {
    const html = fs.readFileSync(path.join(root, directory, file), 'utf8')
    const theme = html.indexOf('js/theme.js')
    const stylesheet = html.indexOf('css/main.css')
    assert.ok(theme >= 0 && theme < stylesheet, `${directory}/${file}: theme must load before stylesheet`)
  }
}

const source = fs.readFileSync(path.join(root, 'js/theme.js'), 'utf8')
function initialTheme(saved, prefersDark, storageFails = false) {
  let theme
  const context = {
    document: { documentElement: { setAttribute: (_, value) => { theme = value } } },
    localStorage: { getItem: () => { if (storageFails) throw new Error('blocked'); return saved } },
    window: { matchMedia: () => ({ matches: prefersDark }) },
  }
  vm.runInNewContext(source, context)
  return theme
}
assert.equal(initialTheme('dark', false), 'dark')
assert.equal(initialTheme('light', true), 'light')
assert.equal(initialTheme(null, true), 'dark')
assert.equal(initialTheme(null, false), 'light')
assert.equal(initialTheme(null, true, true), 'dark')
console.log('Theme initialization passes for every page and preference')
