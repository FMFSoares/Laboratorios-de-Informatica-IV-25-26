import api from './api.js'

export const getLojas = (params) => api.get('/lojas', { params })
export const getLoja = (id) => api.get(`/lojas/${id}`)
