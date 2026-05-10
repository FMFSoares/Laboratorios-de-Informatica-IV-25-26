import api from './api.js'

export const getFaturas = (params) => api.get('/faturas', { params })
export const getFatura = (id) => api.get(`/faturas/${id}`)
export const emitirFatura = (body) => api.post('/faturas', body)
