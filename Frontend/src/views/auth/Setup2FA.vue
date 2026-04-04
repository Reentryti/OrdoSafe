<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-icon">&#128272;</div>
          <h2>Configuration 2FA</h2>
          <p>Scannez le QR code avec votre application d'authentification</p>
        </div>
        <div class="auth-body">
          <!-- Step 1: QR Code -->
          <div v-if="!backupCodes">
            <div v-if="loading" class="loading">Chargement...</div>
            <div v-else>
              <div class="qr-container">
                <img :src="'data:image/png;base64,' + qrImage" alt="QR Code 2FA" v-if="qrImage" />
              </div>

              <div class="secret-key" v-if="secretKey">
                <p>Clé secrète (saisie manuelle) :</p>
                <code>{{ secretKey }}</code>
              </div>

              <div v-if="error" class="alert alert-error">{{ error }}</div>

              <form @submit.prevent="handleConfirm">
                <div class="form-group">
                  <label>Entrez le code généré par votre app</label>
                  <input v-model="token" type="text" inputmode="numeric" maxlength="6" placeholder="000000" class="otp-input" required />
                </div>
                <button type="submit" class="btn-submit" :disabled="confirming">
                  {{ confirming ? 'Vérification...' : 'Activer la 2FA' }}
                </button>
              </form>
            </div>
          </div>

          <!-- Step 2: Backup Codes -->
          <div v-else>
            <div class="backup-section">
              <h3>Codes de secours</h3>
              <p>Conservez ces codes en lieu sûr. Ils vous permettront de vous connecter si vous perdez l'accès à votre application 2FA.</p>
              <div class="codes-grid">
                <div v-for="code in backupCodes" :key="code" class="code-item">{{ code }}</div>
              </div>
              <button @click="goToDashboard" class="btn-submit">Continuer vers le dashboard</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { setup2FA, confirm2FA } from "@/services/auth";
import { useAuthStore } from "@/stores/auth";

const qrImage = ref("");
const secretKey = ref("");
const token = ref("");
const error = ref("");
const loading = ref(true);
const confirming = ref(false);
const backupCodes = ref(null);
const router = useRouter();
const { state } = useAuthStore();

onMounted(async () => {
  try {
    const data = await setup2FA();
    qrImage.value = data.qr_code_image;
    secretKey.value = data.secret_key;
  } catch {
    error.value = "Erreur lors du chargement";
  } finally {
    loading.value = false;
  }
});

async function handleConfirm() {
  error.value = "";
  confirming.value = true;
  try {
    const data = await confirm2FA(token.value);
    backupCodes.value = data.backup_codes;
  } catch (err) {
    error.value = err.data?.error || "Code incorrect";
  } finally {
    confirming.value = false;
  }
}

function goToDashboard() {
  const role = state.user?.role || "doctor";
  router.push(`/${role}/dashboard`);
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
.auth-container { width: 100%; max-width: 480px; }
.auth-card {
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}
.auth-header {
  background: linear-gradient(135deg, #4b6cb7, #182848);
  padding: 2rem;
  text-align: center;
  color: #fff;
}
.auth-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.auth-header h2 { font-size: 1.4rem; font-weight: 700; margin: 0; }
.auth-header p { margin: 0.25rem 0 0; opacity: 0.85; font-size: 0.85rem; }
.auth-body { padding: 2rem; }
.qr-container {
  text-align: center;
  margin-bottom: 1.5rem;
}
.qr-container img {
  width: 200px;
  height: 200px;
  border-radius: 12px;
  border: 3px solid #e0e0e0;
}
.secret-key {
  text-align: center;
  margin-bottom: 1.5rem;
}
.secret-key p { font-size: 0.85rem; color: #666; }
.secret-key code {
  background: #f0f2f5;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.4rem; font-size: 0.9rem; }
.form-group input {
  width: 100%; padding: 0.8rem; border: 2px solid #e0e0e0;
  border-radius: 10px; font-size: 1rem; transition: border-color 0.2s;
}
.form-group input:focus { outline: none; border-color: #4e73df; }
.otp-input { text-align: center; font-size: 1.5rem; letter-spacing: 0.5rem; font-weight: 700; }
.btn-submit {
  width: 100%; padding: 0.9rem; background: linear-gradient(135deg, #4b6cb7, #182848);
  color: #fff; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600;
  cursor: pointer; margin-top: 0.5rem;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.9rem; }
.loading { text-align: center; color: #666; padding: 2rem; }
.backup-section { text-align: center; }
.backup-section h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
.backup-section > p { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
.codes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.code-item {
  background: #f0f2f5;
  padding: 0.6rem;
  border-radius: 8px;
  font-family: monospace;
  font-weight: 700;
  font-size: 1rem;
}
</style>
