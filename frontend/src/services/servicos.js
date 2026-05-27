import api from './api.js'

export const getServicos   = (params)     => api.get('/servicos/', { params })
export const getServico    = (id)         => api.get(`/servicos/${id}`)
export const createServico = (body)       => api.post('/servicos/', body)
export const updateServico = (id, body)   => api.patch(`/servicos/${id}`, body)
