import assert from 'node:assert/strict'
import { normalizeServerUrl } from '../src/services/server-url.js'

assert.equal(normalizeServerUrl('http://192.168.1.2:5001/espada/'), 'http://192.168.1.2:5001/espada')
assert.equal(normalizeServerUrl('https://example.com/'), 'https://example.com')
for (const invalid of ['localhost:5001', 'ftp://example.com', 'http://user:pass@example.com', 'http://example.com/?token=secret']) {
  assert.throws(() => normalizeServerUrl(invalid))
}
