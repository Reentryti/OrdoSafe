<template>
  <div class="auth-page doctor">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header doctor">
          <div class="auth-icon">&#128105;&#8205;&#9877;&#65039;</div>
          <h2>Inscription Médecin</h2>
          <p>Créez votre compte professionnel</p>
        </div>
        <div class="auth-body">
          <div v-if="error" class="alert alert-error">{{ error }}</div>
          <div v-if="errors" class="alert alert-error">
            <div v-for="(msgs, field) in errors" :key="field">
              <strong>{{ field }}:</strong> {{ msgs.join(', ') }}
            </div>
          </div>

          <form @submit.prevent="handleSubmit">
            <h4 class="section-title">Informations personnelles</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Prénom</label>
                <input v-model="form.first_name" type="text" required />
              </div>
              <div class="form-group">
                <label>Nom</label>
                <input v-model="form.last_name" type="text" required />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Date de naissance</label>
                <input v-model="form.date_birth" type="date" required />
              </div>
              <div class="form-group">
                <label>Téléphone</label>
                <input v-model="form.phone_number" type="tel" placeholder="+221 77 777 77 77" />
              </div>
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" type="email" required />
            </div>

            <h4 class="section-title">Informations professionnelles</h4>
            <div class="form-row">
              <div class="form-group">
                <label>N° de licence</label>
                <input v-model="form.licence_number" type="text" required />
              </div>
              <div class="form-group">
                <label>Spécialisation</label>
                <input v-model="form.specialisation" type="text" required />
              </div>
            </div>

            <h4 class="section-title">Sécurité</h4>
            <div class="form-group">
              <label>Mot de passe</label>
              <input v-model="form.password1" type="password" required />
            </div>
            <div class="form-group">
              <label>Confirmer le mot de passe</label>
              <input v-model="form.password2" type="password" required />
            </div>
            <div class="form-group">
              <label>Méthode 2FA</label>
              <select v-model="form.two_factor_method">
                <option value="email">Email</option>
                <option value="sms">SMS</option>
              </select>
            </div>

            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? 'Inscription...' : "S'inscrire" }}
            </button>
          </form>

          <div class="auth-footer">
            <p>Déjà un compte ? <router-link to="/login/doctor">Se connecter</router-link></p>
            <router-link to="/" class="back-link">Retour à l'accueil</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { signup, fetchCsrfToken } from "@/services/auth";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const { setUser } = useAuthStore();
const loading = ref(false);
const error = ref("");
const errors = ref(null);

const form = reactive({
  first_name: "", last_name: "", date_birth: "", email: "", phone_number: "",
  licence_number: "", specialisation: "", password1: "", password2: "", two_factor_method: "email",
});

async function handleSubmit() {
  error.value = "";
  errors.value = null;
  loading.value = true;
  try {
    await fetchCsrfToken();
    const data = await signup("doctor", form);
    setUser(data);
    if (data.needs_2fa_setup) {
      router.push("/setup-2fa");
    } else {
      router.push("/doctor/dashboard");
    }
  } catch (err) {
    if (err.data?.errors) {
      errors.value = err.response.data.errors;
    } else {
      error.value = err.data?.error || "Erreur lors de l'inscription";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem;
}
.auth-page.doctor { background: linear-gradient(135deg, #667eea, #764ba2); }
.auth-container { width: 100%; max-width: 540px; }
.auth-card {
  background: rgba(255,255,255,0.97); border-radius: 20px; overflow: hidden;
  box-shadow: 0 20px 50px rgba(0,0,0,0.15);
}
.auth-header { padding: 2rem; text-align: center; color: #fff; }
.auth-header.doctor { background: linear-gradient(135deg, #4e73df, #224abe); }
.auth-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.auth-header h2 { font-size: 1.4rem; font-weight: 700; margin: 0; }
.auth-header p { margin: 0.25rem 0 0; opacity: 0.85; font-size: 0.85rem; }
.auth-body { padding: 2rem; }
.section-title { font-size: 0.95rem; font-weight: 700; color: #4e73df; margin: 1.25rem 0 0.75rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
.section-title:first-child { margin-top: 0; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { margin-bottom: 0.75rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.3rem; font-size: 0.85rem; }
.form-group input, .form-group select {
  width: 100%; padding: 0.65rem 0.8rem; border: 2px solid #e0e0e0;
  border-radius: 8px; font-size: 0.95rem; transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus { outline: none; border-color: #4e73df; }
.btn-submit {
  width: 100%; padding: 0.85rem; background: linear-gradient(135deg, #4e73df, #224abe);
  color: #fff; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600;
  cursor: pointer; margin-top: 0.75rem;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.85rem; }
.auth-footer { text-align: center; margin-top: 1.25rem; font-size: 0.9rem; }
.auth-footer a { color: #4e73df; text-decoration: none; font-weight: 600; }
.back-link { display: inline-block; margin-top: 0.5rem; color: #999 !important; font-weight: 400 !important; }
</style>
