import api from './api.js'

export const getStock = (lojaId, params) => api.get(`/stock/${lojaId}`, { params })
export const registarEntrada = (lojaId, body) => api.post(`/stock/${lojaId}/entrada`, body)
export const transferirStock = (body) => api.post('/stock/transferencia', body)
