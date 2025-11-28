import axios from 'axios';

const API = axios.create({ 
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
});

export const getClaims = () => API.get('/claims').then(res => res.data);
export const getVerifications = () => API.get('/verifications').then(res => res.data);
export const getItems = () => API.get('/items').then(res => res.data);
