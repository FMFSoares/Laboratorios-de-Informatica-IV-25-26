import api from './api.js'

export const getUtilizadores = (params) => api.get('/utilizadores', { params })
export const createUtilizador = (body) => api.post('/utilizadores', body)
