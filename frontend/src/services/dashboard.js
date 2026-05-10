import api from './api.js'

export const getDashboard = (params) => api.get('/dashboard', { params })
