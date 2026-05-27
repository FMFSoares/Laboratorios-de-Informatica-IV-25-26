import api from './api.js'

export const getLojas    = (params)     => api.get('/lojas/', { params })
export const getLoja     = (id)         => api.get(`/lojas/${id}`)
export const createLoja  = (body)       => api.post('/lojas/', body)
export const updateLoja  = (id, body)   => api.patch(`/lojas/${id}`, body)
