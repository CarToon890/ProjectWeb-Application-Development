// Apply the saved theme before the stylesheet can paint the page.
(() => {
  let saved
  try {
    saved = localStorage.getItem('theme')
  } catch (_) {
    // Storage can be unavailable in private or restricted browsing contexts.
  }

  const systemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  const theme = saved === 'dark' || saved === 'light' ? saved : (systemDark ? 'dark' : 'light')
  document.documentElement.setAttribute('data-theme', theme)
})()
