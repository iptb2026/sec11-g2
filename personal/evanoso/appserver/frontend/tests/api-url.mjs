import assert from 'node:assert/strict'
import { normalizeApiUrl } from '../src/utils/api-url.js'

assert.equal(normalizeApiUrl(' http://192.168.1.20:5001 '), 'http://192.168.1.20:5001/')
assert.equal(normalizeApiUrl('https://demo.example/bembank'), 'https://demo.example/bembank/')
assert.throws(() => normalizeApiUrl('ftp://192.168.1.20'))
assert.throws(() => normalizeApiUrl('http://user:pass@192.168.1.20'))
