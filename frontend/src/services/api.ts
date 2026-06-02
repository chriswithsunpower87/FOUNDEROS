/**
 * File: src/services/api.ts
 * Purpose: Configured Axios instance with auth interceptors.
 * Responsibilities:
 *   - Set base URL from environment variable
 *   - Attach Authorization header from localStorage on every request
 *   - Handle 401 responses by clearing auth state
 */

import axios from "axios";
import { API_BASE_URL } from "@/lib/constants";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

/** Request interceptor — attach JWT from localStorage */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Response interceptor — handle auth expiry */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored token and redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
