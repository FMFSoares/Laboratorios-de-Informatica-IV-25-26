import api from './api.js'

export const getClientes = (params) => api.get('/clientes', { params })
export const getCliente = (id) => api.get(`/clientes/${id}`)
export const createCliente = (body) => api.post('/clientes', body)
export const updateCliente = (id, body) => api.patch(`/clientes/${id}`, body)
export const getClienteHistorico = (id) => api.get(`/clientes/${id}/historico`)
