import api from "../api/axios";

// Login api calll
export async function login(username, password) {
  const res = await api.post("/api/token/", { username, password });
  return res.data;
}

// Logout api call
export async function logout() {
  await api.post("/api/logout/");
}


export async function isAuthenticated() {
  try {
    await api.get("/api/user/"); 
    return true;
  } catch {
    return false;
  }
}
