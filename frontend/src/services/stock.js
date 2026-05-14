import api from './api.js'

export const getStock = (params) => api.get('/stock', { params })
export const registarEntrada = (body) => api.post('/stock/entradas', body)
export const transferirStock = (body) => api.post('/stock/transferencias', body)
export const updateStockMinimo = (pecaId, body) => api.patch(`/stock/${pecaId}/minimo`, body)
