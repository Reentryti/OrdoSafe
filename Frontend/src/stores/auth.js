import { reactive, readonly } from "vue";
import { getCurrentUser, logout as apiLogout, fetchCsrfToken } from "@/services/auth";

const state = reactive({
  user: null,
  loading: true,
  initialized: false,
});

export function useAuthStore() {
  async function init() {
    if (state.initialized) return;
    state.loading = true;
    try {
      await fetchCsrfToken();
      state.user = await getCurrentUser();
    } catch {
      state.user = null;
    } finally {
      state.loading = false;
      state.initialized = true;
    }
  }

  function setUser(user) {
    state.user = user;
    state.initialized = true;
  }

  async function logout() {
    try {
      await apiLogout();
    } catch {
      // ignore
    }
    state.user = null;
  }

  return {
    state: readonly(state),
    init,
    setUser,
    logout,
  };
}
