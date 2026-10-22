import assert from 'node:assert/strict'
import { accountQrPayload, parseBankQr } from '../frontend/src/utils/bank-qr.js'
const account = { account_number: 'BEM100000001', currency_code: 'PHP' }
assert.deepEqual(parseBankQr(accountQrPayload(account, '125.50')), { account_number: account.account_number, amount: '125.50' })
assert.deepEqual(parseBankQr(accountQrPayload(account)), { account_number: account.account_number, amount: '' })
for (const text of ['https://example.com', '{}', 'null', 'x'.repeat(2049)]) assert.throws(() => parseBankQr(text))
for (const changes of [{bank:'Other'}, {currency_code:'USD'}, {account_number:'<script>'}, {amount:-1}, {amount:'0'}, {amount:'1.001'}, {amount:'1e3'}]) {
  assert.throws(() => parseBankQr(JSON.stringify({bank:'Bembank',...account,...changes})))
}
console.log('PASS QR payload round trips and rejects invalid payment data')
