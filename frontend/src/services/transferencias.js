import api from './api.js'

export const getTransferencias    = (params) => api.get('/transferencias/', { params }).then(r => r.data)
export const getTransferencia     = (id)     => api.get(`/transferencias/${id}`).then(r => r.data)
export const criarTransferencia   = (body)   => api.post('/transferencias/', body).then(r => r.data)
export const responderTransferencia = (id, body) => api.post(`/transferencias/${id}/responder`, body).then(r => r.data)
export const confirmarRecepcao    = (id)     => api.post(`/transferencias/${id}/confirmar-recepcao`).then(r => r.data)
export const cancelarTransferencia = (id)   => api.post(`/transferencias/${id}/cancelar`).then(r => r.data)
export const getPdfTransferencia  = (id)     => api.get(`/transferencias/${id}/pdf`, { responseType: 'arraybuffer' }).then(r => r.data)
