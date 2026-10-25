export function normalizeServerUrl (address) {
  let url
  try { url = new URL(address) } catch { throw new Error('Enter a valid server address.') }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error('Use an http:// or https:// server address without a username, password, query, or fragment.')
  }
  return url.href.replace(/\/+$/, '')
}
