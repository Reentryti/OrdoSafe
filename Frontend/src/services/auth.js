import api from "@/api/http";

export async function login(role, email, password) {
  return api.post(`/api/v1/auth/${role}/login/`, { email, password });
}

export async function verify2FA(token) {
  return api.post("/api/v1/auth/verify-2fa/", { token });
}

export async function setup2FA() {
  return api.get("/api/v1/auth/setup-2fa/");
}

export async function confirm2FA(token) {
  return api.post("/api/v1/auth/setup-2fa/", { token });
}

export async function signup(role, data) {
  return api.post(`/api/v1/auth/${role}/signup/`, data);
}

export async function getCurrentUser() {
  return api.get("/api/v1/auth/me/");
}

export async function logout() {
  return api.post("/api/v1/auth/logout/");
}

export async function fetchCsrfToken() {
  return api.get("/api/v1/auth/csrf/");
}

export async function isAuthenticated() {
  try {
    await api.get("/api/v1/auth/me/");
    return true;
  } catch {
    return false;
  }
}
