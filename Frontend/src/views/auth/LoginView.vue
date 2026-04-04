<template>
  <div class="auth-page" :class="role">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header" :class="role">
          <div class="auth-icon">{{ role === 'doctor' ? '&#128105;&#8205;&#9877;&#65039;' : '&#128138;' }}</div>
          <h2>{{ role === 'doctor' ? 'Espace Médecin' : 'Espace Pharmacien' }}</h2>
          <p>Connectez-vous à votre compte</p>
        </div>

        <div class="auth-body">
          <div v-if="error" class="alert alert-error">{{ error }}</div>

          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>Adresse email</label>
              <input v-model="email" type="email" placeholder="email@exemple.com" required />
            </div>

            <div class="form-group">
              <label>Mot de passe</label>
              <input v-model="password" type="password" placeholder="Votre mot de passe" required />
            </div>

            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? 'Connexion...' : 'Se connecter' }}
            </button>
          </form>

          <div class="auth-footer">
            <p>
              Pas encore de compte ?
              <router-link :to="`/signup/${role}`">Créer un compte</router-link>
            </p>
            <router-link to="/" class="back-link">Retour à l'accueil</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login, fetchCsrfToken } from "@/services/auth";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({ role: { type: String, required: true } });

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const router = useRouter();
const { setUser } = useAuthStore();

async function handleSubmit() {
  error.value = "";
  loading.value = true;
  try {
    await fetchCsrfToken();
    const data = await login(props.role, email.value, password.value);

    if (data.requires_2fa) {
      router.push({ name: "Verify2FA", query: { role: props.role } });
    } else {
      setUser(data);
      router.push(`/${props.role}/dashboard`);
    }
  } catch (err) {
    const msg = err.data?.error;
    error.value = msg || "Erreur lors de la connexion";
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
}
.auth-page.doctor {
  background: linear-gradient(135deg, #667eea, #764ba2);
}
.auth-page.pharmacist {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}
.auth-container {
  width: 100%;
  max-width: 440px;
}
.auth-card {
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}
.auth-header {
  padding: 2.5rem 2rem;
  text-align: center;
  color: #fff;
}
.auth-header.doctor {
  background: linear-gradient(135deg, #4e73df, #224abe);
}
.auth-header.pharmacist {
  background: linear-gradient(135deg, #1cc88a, #13855c);
}
.auth-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}
.auth-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}
.auth-header p {
  margin: 0.25rem 0 0;
  opacity: 0.85;
  font-size: 0.9rem;
}
.auth-body {
  padding: 2rem;
}
.form-group {
  margin-bottom: 1.25rem;
}
.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}
.form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s;
}
.form-group input:focus {
  outline: none;
  border-color: #4e73df;
}
.btn-submit {
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(135deg, #4e73df, #224abe);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 0.5rem;
}
.btn-submit:hover {
  opacity: 0.9;
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.alert {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.alert-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
}
.auth-footer a {
  color: #4e73df;
  text-decoration: none;
  font-weight: 600;
}
.auth-footer a:hover {
  text-decoration: underline;
}
.back-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #999 !important;
  font-weight: 400 !important;
}
</style>
