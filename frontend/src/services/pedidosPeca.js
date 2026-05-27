import api from './api.js'

export const getPedidosPeca    = (params) => api.get('/pedidos-peca/', { params }).then(r => r.data)
export const criarPedidoPeca   = (body)   => api.post('/pedidos-peca/', body).then(r => r.data)
export const responderPedidoPeca = (id, body) => api.post(`/pedidos-peca/${id}/responder`, body).then(r => r.data)
