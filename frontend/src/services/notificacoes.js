import api from './api.js'

export const getNotificacoes = (params) => api.get('/notificacoes/', { params }).then(r => r.data)
export const countNaoLidas   = ()       => api.get('/notificacoes/count').then(r => r.data)
export const marcarLida      = (id)     => api.post(`/notificacoes/${id}/ler`)
export const marcarTodasLidas = ()      => api.post('/notificacoes/ler-todas')
export const apagarTodas      = ()      => api.delete('/notificacoes/')
