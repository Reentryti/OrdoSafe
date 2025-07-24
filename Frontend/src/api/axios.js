import axios from "axios";

// Define Api call 
const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Token error management
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Non autorisé (JWT manquant ou expiré)");
      //Redirecting
    }
    return Promise.reject(error);
  }
);

export default api;
