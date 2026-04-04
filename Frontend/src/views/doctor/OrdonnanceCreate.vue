<template>
  <div class="page">
    <div class="page-container">
      <div class="page-header">
        <h1>Nouvelle Ordonnance</h1>
        <p>Créez une prescription médicale sécurisée</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="errors" class="alert alert-error">
        <div v-for="(msgs, field) in errors" :key="field">
          <strong>{{ field }}:</strong> {{ Array.isArray(msgs) ? msgs.join(', ') : msgs }}
        </div>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-grid">
          <!-- Patient -->
          <div class="form-card">
            <h3>Informations Patient</h3>
            <div class="form-row">
              <div class="form-group">
                <label>Prénom</label>
                <input v-model="form.patient_first_name" type="text" required />
              </div>
              <div class="form-group">
                <label>Nom</label>
                <input v-model="form.patient_last_name" type="text" required />
              </div>
            </div>
            <div class="form-group">
              <label>Date de naissance</label>
              <input v-model="form.patient_date_birth" type="date" required />
            </div>
            <div class="form-group">
              <label>Téléphone</label>
              <input v-model="form.patient_phone" type="tel" placeholder="+221 77 777 77 77" required />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.patient_email" type="email" required />
            </div>
          </div>

          <!-- Doctor info -->
          <div class="form-card">
            <h3>Médecin Prescripteur</h3>
            <div class="doctor-display">
              <div class="doctor-avatar">Dr</div>
              <div>
                <strong>{{ state.user?.full_name }}</strong>
                <p>{{ state.user?.email }}</p>
                <p v-if="state.user?.specialisation">{{ state.user.specialisation }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Medications -->
        <div class="form-card">
          <h3>Prescription Médicamenteuse</h3>
          <p class="hint">Saisissez les médicaments séparés par des virgules ou un par ligne</p>
          <div class="form-group">
            <textarea v-model="form.medicaments" rows="5" placeholder="Paracétamol 500mg, Ibuprofène 400mg" required></textarea>
          </div>
          <div class="example-btns">
            <button type="button" @click="addJsonExample" class="btn-example">Exemple JSON</button>
            <button type="button" @click="addSimpleExample" class="btn-example">Exemple simple</button>
          </div>
        </div>

        <!-- Notes -->
        <div class="form-card">
          <h3>Instructions complémentaires</h3>
          <div class="form-group">
            <textarea v-model="form.notes" rows="3" placeholder="Notes et recommandations..."></textarea>
          </div>
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <router-link to="/doctor/dashboard" class="btn-cancel">Annuler</router-link>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? 'Création...' : 'Créer l\'ordonnance' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { createOrdonnance } from "@/services/ordonnance";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const { state } = useAuthStore();
const loading = ref(false);
const error = ref("");
const errors = ref(null);

const form = reactive({
  patient_first_name: "", patient_last_name: "", patient_date_birth: "",
  patient_phone: "", patient_email: "", medicaments: "", notes: "",
});

async function handleSubmit() {
  error.value = "";
  errors.value = null;
  loading.value = true;
  try {
    const data = await createOrdonnance(form);
    router.push(`/doctor/ordonnance/${data.id}`);
  } catch (err) {
    if (err.data?.errors) {
      errors.value = err.response.data.errors;
    } else {
      error.value = err.data?.error || "Erreur lors de la création";
    }
  } finally {
    loading.value = false;
  }
}

function addJsonExample() {
  form.medicaments = `Paracétamol 500mg - 3 fois par jour - 7 jours\nIbuprofène 400mg - Matin et soir - 5 jours`;
}
function addSimpleExample() {
  form.medicaments = "Paracétamol 500mg, Ibuprofène 400mg, Amoxicilline 1g";
}
</script>

<style scoped>
.page { padding: 2rem; }
.page-container { max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.6rem; color: #1a1a2e; margin: 0; }
.page-header p { color: #666; margin: 0.25rem 0 0; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
.form-card {
  background: #fff; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.25rem;
}
.form-card h3 { font-size: 1.05rem; color: #1a1a2e; margin: 0 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { margin-bottom: 0.75rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.3rem; font-size: 0.85rem; }
.form-group input, .form-group textarea {
  width: 100%; padding: 0.65rem 0.8rem; border: 2px solid #e0e0e0;
  border-radius: 8px; font-size: 0.95rem; resize: vertical; font-family: inherit;
}
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #4e73df; }
.hint { font-size: 0.85rem; color: #666; margin-bottom: 0.75rem; }
.example-btns { display: flex; gap: 0.5rem; }
.btn-example {
  background: #e3f2fd; color: #1565c0; border: none; padding: 0.4rem 0.8rem;
  border-radius: 20px; font-size: 0.8rem; cursor: pointer; font-weight: 600;
}
.btn-example:hover { background: #bbdefb; }
.doctor-display { display: flex; align-items: center; gap: 1rem; background: #f8f9fc; padding: 1rem; border-radius: 10px; }
.doctor-avatar {
  width: 48px; height: 48px; background: #4e73df; color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem;
}
.doctor-display p { margin: 0.15rem 0; font-size: 0.85rem; color: #666; }
.form-actions { display: flex; justify-content: space-between; margin-top: 1rem; }
.btn-cancel {
  padding: 0.75rem 1.5rem; background: #e9ecef; color: #495057; border-radius: 10px;
  text-decoration: none; font-weight: 600;
}
.btn-submit {
  padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #4e73df, #224abe);
  color: #fff; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.95rem;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.85rem; }
</style>
