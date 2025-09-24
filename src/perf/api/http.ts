import axios from 'axios';

const baseURL = import.meta.env.VITE_PERF_API_BASE || 'http://127.0.0.1:8002';

export const http = axios.create({
  baseURL,
  timeout: 15000,
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err?.response?.status, err?.message);
    return Promise.reject(err);
  }
);
