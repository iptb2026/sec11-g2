import { reactive } from 'vue'

const state = reactive({ items: [] })

function seed() {
  if (state.items.length === 0) {
    state.items.push({ id: Date.now(), title: 'Demo: System ready', body: 'The system is ready for demo.', read: false, created_at: new Date().toISOString() })
  }
}

function list() {
  seed()
  return state.items
}

function add(title, body) {
  const it = { id: Date.now()+Math.random(), title, body, read: false, created_at: new Date().toISOString() }
  state.items.unshift(it)
  return it
}

function markRead(id) {
  const it = state.items.find(x => x.id === id)
  if (it) it.read = true
}

function unreadCount() {
  return state.items.filter(i => !i.read).length
}

export default { list, add, markRead, unreadCount }
