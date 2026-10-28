// Run against tests/browser_api.py and the Quasar preview. Never uses the bank database.
const { chromium } = require('playwright');
const { createHmac } = require('node:crypto');
const assert = require('node:assert/strict');
let debugPage;
function totp(secret) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  const bits = [...secret].map(c => alphabet.indexOf(c).toString(2).padStart(5, '0')).join('');
  const key = Buffer.from((bits.match(/.{8}/g) || []).map(b => parseInt(b, 2)));
  const counter = Buffer.alloc(8); counter.writeBigUInt64BE(BigInt(Math.floor(Date.now() / 30000)));
  const hash = createHmac('sha1', key).update(counter).digest(); const offset = hash[19] & 15;
  return String((hash.readUInt32BE(offset) & 0x7fffffff) % 1000000).padStart(6, '0');
}
(async () => {
  const browser = await chromium.launch({ headless: process.env.BEMBANK_HEADED !== '1', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  debugPage = page;
  page.setDefaultTimeout(20000);
  const browserErrors = [], badResponses = []; let setupSecret;
  page.on('pageerror', error => browserErrors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') browserErrors.push(message.text()); });
  await page.route('**/bembank/api/**', async route => {
    const path = new URL(route.request().url()).pathname.replace('/bembank/api', '');
    const response = await route.fetch({ url: 'http://127.0.0.1:5012' + path });
    if (response.status() >= 400) { badResponses.push(path + ': ' + response.status()); console.log('Failed test API response:', path, response.status()); }
    if (path === '/auth/otp/setup' && response.ok()) setupSecret = (await response.json()).secret;
    await route.fulfill({ response });
  });
  const goto = async path => { const link = page.locator(`a[href="#${path}"]`).first(); if (page.viewportSize().width >= 1024 && await link.isVisible()) await link.click(); else { await page.goto('http://127.0.0.1:9000/bembank/#' + path); await page.reload(); } const titles = { '/requests': 'Deposits & withdrawals', '/customer/cards': 'My cards', '/my-account': 'My accounts', '/customer/transfers': 'Send funds', '/customer/bill-payments': 'Pay bills', '/my-transactions': 'Transactions', '/customer/notifications': 'Activity alerts', '/profile': 'Profile & security' }; if (titles[path]) await page.getByRole('heading', { name: titles[path], exact: true }).waitFor(); await page.waitForLoadState('networkidle'); };
  const choose = async label => { await page.getByLabel(label, { exact: true }).click(); await page.getByRole('option').first().click(); };
  const signIn = async () => { await goto('/login'); await page.getByLabel('Username', { exact: true }).fill('alice'); await page.getByLabel('Password', { exact: true }).fill('test-password-123'); await page.getByRole('button', { name: 'Sign in', exact: true }).click(); };
  await signIn(); await page.getByRole('heading', { name: /Welcome back,/ }).waitFor();
  console.log('PASS: password login and overview');

  await goto('/requests'); await choose('Account');
  await page.getByLabel('Amount (PHP)', { exact: true }).fill('500');
  await page.getByRole('button', { name: 'Submit request', exact: true }).click();
  await page.locator('td').filter({ hasText: /^PENDING$/ }).waitFor();
  const staffLogin = await page.request.post('http://127.0.0.1:5012/auth/login', { form: { username: 'staff', password: 'test-password-123' } });
  const staffHeaders = { Authorization: 'Bearer ' + (await staffLogin.json()).access_token };
  const requests = await (await page.request.get('http://127.0.0.1:5012/banking-requests/', { headers: staffHeaders })).json();
  assert.equal((await page.request.post(`http://127.0.0.1:5012/banking-requests/${requests[0].id}/review`, { headers: staffHeaders, data: { status: 'APPROVED' } })).status(), 200);
  await page.getByRole('button', { name: 'Refresh', exact: true }).click(); await page.locator('td').filter({ hasText: /^APPROVED$/ }).waitFor();
  console.log('PASS: deposit request, staff processing, customer status refresh');

  await goto('/customer/cards'); await page.getByRole('button', { name: 'Create card' }).click(); await choose('Choose an account');
  await page.getByRole('button', { name: 'Create card', exact: true }).click(); await page.getByText('VIRTUAL', { exact: true }).waitFor();
  await page.getByLabel('Freeze card', { exact: true }).click(); await page.locator('.virtual-card').getByText('FROZEN', { exact: true }).waitFor();
  await page.getByLabel('Freeze card', { exact: true }).click(); await page.locator('.virtual-card').getByText('ACTIVE', { exact: true }).waitFor();
  await page.getByText('Spending limit', { exact: true }).click(); await page.getByRole('dialog').locator('input').fill('1500'); await page.getByRole('button', { name: 'OK', exact: true }).click();
  await page.getByText('₱ 1,500', { exact: true }).waitFor();
  await page.getByText('Set PIN', { exact: true }).click(); await page.getByLabel('Current password', { exact: true }).fill('test-password-123'); await page.getByLabel('New six-digit PIN').fill('246810');
  await page.getByRole('button', { name: 'Save PIN', exact: true }).click(); await page.getByText('Change PIN', { exact: true }).waitFor();
  await page.getByText('Report lost card', { exact: true }).click(); await page.getByRole('button', { name: 'OK', exact: true }).click(); await page.locator('.virtual-card').getByText('LOST', { exact: true }).waitFor();
  console.log('PASS: card creation, freeze/unfreeze, limit, PIN, lost-card report');

  await goto('/my-account'); await page.getByRole('button', { name: 'Receive', exact: true }).click(); await page.getByAltText('QR code with account details').waitFor(); await page.getByRole('button', { name: 'Close', exact: true }).click();
  await page.getByRole('button', { name: 'Request an account' }).click(); await choose('Account type'); await page.getByRole('button', { name: 'Submit application' }).click(); await page.locator('td').filter({ hasText: /^PENDING$/ }).waitFor();
  console.log('PASS: account details, receive QR, account application');

  await goto('/customer/transfers'); await choose('From account'); await page.getByLabel('To account number').fill('BEM0002'); await page.getByLabel('Amount (PHP)', { exact: true }).fill('125.50');
  await page.getByRole('button', { name: 'Save this recipient' }).click(); await page.getByRole('dialog').locator('input').fill('Bob'); await page.getByRole('button', { name: 'OK', exact: true }).click();
  await page.getByLabel('Choose a saved recipient').waitFor();
  await page.getByRole('button', { name: 'Review transfer' }).click(); await page.getByRole('heading', { name: 'Confirm your transfer' }).waitFor(); await page.getByRole('button', { name: 'Confirm transfer', exact: true }).click(); await page.getByText('Transfer completed', { exact: true }).waitFor();
  console.log('PASS: saved recipient and confirmed transfer');

  await goto('/customer/bill-payments'); await choose('Pay from account'); await page.getByLabel('Biller', { exact: true }).fill('Electricity'); await page.getByLabel('Customer or invoice reference').fill('INV-100'); await page.getByLabel('Amount (PHP)', { exact: true }).fill('100');
  await page.getByRole('button', { name: 'Review payment' }).click(); await page.getByRole('button', { name: 'Confirm payment' }).click(); await page.getByRole('cell', { name: 'Electricity', exact: true }).waitFor();
  console.log('PASS: confirmed bill payment');

  await goto('/my-transactions'); await page.getByLabel('Search transactions').fill('BILL PAYMENT'); await page.locator('td').filter({ hasText: /^BILL PAYMENT$/ }).waitFor();
  let download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export CSV' }).click(); await download;
  download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Download receipt' }).click(); await download;
  await goto('/customer/notifications'); await page.getByRole('button', { name: 'Mark all as read' }).click(); await page.getByText(/0 unread\./).waitFor(); await page.reload(); await page.getByText(/0 unread\./).waitFor();
  console.log('PASS: transaction search, CSV, receipts, persistent read/unread alerts');

  await goto('/profile'); await page.getByRole('button', { name: 'Edit profile' }).click(); await page.getByLabel('First name', { exact: true }).fill('Alice'); await page.getByLabel('Email', { exact: true }).fill('alice@example.com'); await page.getByRole('button', { name: 'Save profile' }).click(); await page.getByText('alice@example.com', { exact: true }).waitFor();
  await page.getByRole('button', { name: 'Set up authenticator' }).click(); await page.getByRole('dialog').getByLabel('Current password', { exact: true }).fill('test-password-123'); await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await page.getByAltText('Scan to set up Bembank in your authenticator').waitFor(); assert.ok(setupSecret);
  await page.getByLabel('Six-digit code', { exact: true }).fill(totp(setupSecret)); await page.getByRole('button', { name: 'Enable verification' }).click();
  await page.getByRole('heading', { name: 'Save your recovery codes' }).waitFor(); const recovery = await page.locator('.recovery-grid code').allTextContents(); assert.equal(recovery.length, 8);
  download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Download recovery codes' }).click(); await download;
  await page.getByLabel('I saved my recovery codes somewhere safe').check(); await page.getByRole('button', { name: 'Done', exact: true }).click();
  console.log('PASS: profile editing, QR enrollment, confirmed OTP setup, recovery download');
  await page.getByRole('button', { name: 'Sign out', exact: true }).first().click(); await signIn(); await page.getByRole('heading', { name: 'Verify your sign-in' }).waitFor();
  await page.getByRole('button', { name: 'Use a recovery code' }).click(); await page.getByLabel('Recovery code', { exact: true }).fill(recovery[0]); await page.getByRole('button', { name: 'Verify and sign in' }).click(); await page.getByRole('heading', { name: /Welcome back,/ }).waitFor();
  await page.getByRole('button', { name: 'Sign out', exact: true }).first().click(); await signIn(); await page.getByRole('heading', { name: 'Verify your sign-in' }).waitFor();
  // Enrollment consumed the current code. Wait for the next 30-second code.
  await page.waitForTimeout(30100 - Date.now() % 30000);
  await page.getByLabel('Authentication code', { exact: true }).fill(totp(setupSecret)); await page.getByRole('button', { name: 'Verify and sign in' }).click(); await page.getByRole('heading', { name: /Welcome back,/ }).waitFor();
  console.log('PASS: recovery-code login and authenticator-code login');

  await page.setViewportSize({ width: 390, height: 844 });
  for (const path of ['/', '/requests', '/customer/cards', '/customer/notifications', '/profile', '/my-account', '/customer/transfers', '/customer/bill-payments', '/my-transactions']) {
    await goto(path); await page.waitForTimeout(150);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'Overflow: ' + path);
  }
  assert.deepEqual(browserErrors, []); assert.deepEqual(badResponses, []);
  console.log('PASS: all customer menu destinations at mobile width, zero browser errors or failed API responses');
  await browser.close();
})().catch(async error => { console.error(error); if (debugPage) { console.log('Page:', debugPage.url()); console.log('Table cells:', await debugPage.getByRole('cell').allTextContents()); console.log('Form messages:', await debugPage.locator('.q-notification__message, .q-field__messages, .bank-feedback').allTextContents()); } process.exit(1); });
