import api from './api.js'

export const getFaturas = (params) => api.get('/faturas', { params })
export const getFatura = (id) => api.get(`/faturas/${id}`)
export const emitirFatura = (body) => api.post('/faturas', body)
export const enviarEmailFatura = (id, body) => api.post(`/faturas/${id}/enviar-email`, body)
export const downloadFaturaPdf = (id) => api.get(`/faturas/${id}/pdf`, { responseType: 'blob' })
