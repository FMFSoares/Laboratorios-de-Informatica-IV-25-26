import api from './api.js'

export const getAuditoria = (params) => api.get('/auditoria/', { params })
