const STORAGE_KEY = 'bembank-api-base-url'

export function normalizeApiUrl (value) {
  const url = new URL(value.trim())
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error('Enter an HTTP or HTTPS address without credentials, a query, or a fragment.')
  }
  url.pathname = `${url.pathname.replace(/\/$/, '')}/`
  return url.toString()
}

export function savedApiUrl () {
  try { return localStorage.getItem(STORAGE_KEY) || '' } catch { return '' }
}

export function saveApiUrl (value) {
  const normalized = normalizeApiUrl(value)
  localStorage.setItem(STORAGE_KEY, normalized)
  return normalized
}
