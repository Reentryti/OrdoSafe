<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-icon">&#128272;</div>
          <h2>Vérification 2FA</h2>
          <p>Entrez le code de votre application d'authentification</p>
        </div>
        <div class="auth-body">
          <div v-if="error" class="alert alert-error">{{ error }}</div>

          <form @submit.prevent="handleVerify">
            <div class="form-group">
              <label>Code à 6 chiffres</label>
              <input
                v-model="token"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="000000"
                class="otp-input"
                required
              />
            </div>
            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? 'Vérification...' : 'Vérifier' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { verify2FA } from "@/services/auth";
import { useAuthStore } from "@/stores/auth";

const token = ref("");
const error = ref("");
const loading = ref(false);
const router = useRouter();
const route = useRoute();
const { setUser } = useAuthStore();

async function handleVerify() {
  error.value = "";
  loading.value = true;
  try {
    const data = await verify2FA(token.value);
    setUser(data);
    const role = data.role || route.query.role || "doctor";
    router.push(`/${role}/dashboard`);
  } catch (err) {
    error.value = err.data?.error || "Code invalide";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
}
.auth-container { width: 100%; max-width: 420px; }
.auth-card {
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}
.auth-header {
  background: linear-gradient(135deg, #4b6cb7, #182848);
  padding: 2.5rem 2rem;
  text-align: center;
  color: #fff;
}
.auth-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.auth-header h2 { font-size: 1.5rem; font-weight: 700; margin: 0; }
.auth-header p { margin: 0.25rem 0 0; opacity: 0.85; font-size: 0.9rem; }
.auth-body { padding: 2rem; }
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.4rem; }
.form-group input {
  width: 100%; padding: 0.8rem 1rem; border: 2px solid #e0e0e0;
  border-radius: 10px; font-size: 1rem; transition: border-color 0.2s;
}
.form-group input:focus { outline: none; border-color: #4e73df; }
.otp-input { text-align: center; font-size: 1.5rem; letter-spacing: 0.5rem; font-weight: 700; }
.btn-submit {
  width: 100%; padding: 0.9rem; background: linear-gradient(135deg, #4b6cb7, #182848);
  color: #fff; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600;
  cursor: pointer; transition: opacity 0.2s;
}
.btn-submit:hover { opacity: 0.9; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; }
</style>
