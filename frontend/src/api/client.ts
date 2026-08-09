import axios from "axios";
import { clearSession, readSession, saveSession } from "@/lib/session";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const session = readSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

let refreshingPromise: Promise<string | null> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status !== 401 || originalRequest?._retry) {
      return Promise.reject(error);
    }

    const session = readSession();
    if (!session?.refreshToken) {
      clearSession();
      return Promise.reject(error);
    }

    if (!refreshingPromise) {
      refreshingPromise = api
        .post("/auth/refresh", { refresh_token: session.refreshToken })
        .then((response) => {
          const next = saveSession({
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            tokenType: response.data.token_type,
            role: session.role,
          });
          return next.accessToken;
        })
        .catch(() => {
          clearSession();
          return null;
        })
        .finally(() => {
          refreshingPromise = null;
        });
    }

    const nextToken = await refreshingPromise;
    if (!nextToken) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    originalRequest.headers.Authorization = `Bearer ${nextToken}`;
    return api(originalRequest);
  },
);
