import api from './api.js'

export const getUtilizadores    = (params)     => api.get('/utilizadores', { params })
export const getUtilizador      = (id)         => api.get(`/utilizadores/${id}`)
export const createUtilizador   = (body)       => api.post('/utilizadores', body)
export const updateUtilizador   = (id, body)   => api.patch(`/utilizadores/${id}`, body)
export const resetPasswordAdmin = (id, body)   => api.patch(`/utilizadores/${id}/password`, body)
