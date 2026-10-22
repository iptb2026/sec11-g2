export function parseBankQr (text) {
  if (typeof text !== 'string' || text.length > 2048) throw new Error('This is not a Bembank account QR code.')
  let data
  try { data = JSON.parse(text) } catch { throw new Error('Scan a Bembank account QR code, not a website link.') }
  if (!data || String(data.bank).toLowerCase() !== 'bembank' || data.currency_code !== 'PHP' || typeof data.account_number !== 'string' || !/^[A-Za-z0-9-]{1,30}$/.test(data.account_number)) throw new Error('This QR code does not contain valid Bembank account details.')
  const amount = data.amount == null || data.amount === '' ? '' : String(data.amount)
  if (amount && (!/^\d{1,16}(\.\d{1,2})?$/.test(amount) || Number(amount) <= 0)) throw new Error('The requested amount in this QR code is invalid.')
  return { account_number: data.account_number, amount }
}
export function accountQrPayload (account, amount = '') {
  const data = { bank: 'Bembank', version: 1, account_number: account.account_number, currency_code: account.currency_code, ...(amount !== '' ? { amount: String(amount) } : {}) }
  parseBankQr(JSON.stringify(data))
  return JSON.stringify(data)
}
export function downloadText (text, filename) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
  const link = document.createElement('a'); link.href = url; link.download = filename; link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
