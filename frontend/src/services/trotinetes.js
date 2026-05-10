import api from './api.js'

export const getTrotinetes = (params) => api.get('/trotinetes', { params })
export const getTrotinete = (id) => api.get(`/trotinetes/${id}`)
export const createTrotinete = (body) => api.post('/trotinetes', body)
export const updateTrotinete = (id, body) => api.patch(`/trotinetes/${id}`, body)
