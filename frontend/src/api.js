import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const API = axios.create({
  baseURL: API_BASE
});

export async function verifyText(text) {
  const res = await fetch(`${API_BASE}/verify-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  return res.json()
}

export const getClaims = () => API.get('/claims').then(res => res.data);
export const getVerifications = () => API.get('/verifications').then(res => res.data);
export const getItems = () => API.get('/items').then(res => res.data);
