import api from './api'

export async function listUsers() {
  return api.get('/users/')
}

export async function listCustomers() {
  return api.get('/users/customers')
}

export async function createUser(payload) {
  return api.post('/users/', payload)
}

export async function updateUser(id, payload) {
  return api.put(`/users/${id}`, payload)
}

export async function activateUser(id) {
  return api.post(`/users/${id}/activate`)
}

export async function deactivateUser(id) {
  return api.post(`/users/${id}/deactivate`)
}

export async function deleteUser(id) {
  return api.del(`/users/${id}`)
}

export default { listUsers, listCustomers, createUser, updateUser, activateUser, deactivateUser, deleteUser }
