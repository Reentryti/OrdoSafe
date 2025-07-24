// src/composables/useLogin.js
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/api/axios";

export function useLogin() {
  const username = ref("");
  const password = ref("");
  const role = ref("patient");
  const error = ref("");
  const router = useRouter();

  async function handleLogin() {
    error.value = "";
    try {
      //Corresponding API call w/ endpoint 
      const loginUrl = `/api/${role.value}/login/`;
      await api.post(loginUrl, { username: username.value, password: password.value });
      router.push(`/${role.value}/dash`);
    } catch (err) {
      if (err.response?.status === 401) {
        error.value = "Identifiants invalides.";
      } else {
        error.value = "Erreur lors de la connexion. Réessaie.";
      }
    }
  }

  return {
    username,
    password,
    role,
    error,
    handleLogin,
  };
}
