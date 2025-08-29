import axios from 'axios';

// Centralized axios instance to send credentials for cookie-based auth
export const api = axios.create({
  withCredentials: true,
  baseURL: '',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// Optional: response interceptor for global error handling
api.interceptors.response.use(
  (res) => res,
  (err) => {
    return Promise.reject(err);
  }
);


