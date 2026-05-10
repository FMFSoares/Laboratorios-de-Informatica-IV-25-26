import api from './api.js'

export const getPecas = (params) => api.get('/pecas', { params })
export const getPeca = (id) => api.get(`/pecas/${id}`)
export const createPeca = (body) => api.post('/pecas', body)
export const updatePeca = (id, body) => api.patch(`/pecas/${id}`, body)
