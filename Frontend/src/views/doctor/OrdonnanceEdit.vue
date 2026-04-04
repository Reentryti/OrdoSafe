<template>
  <div class="page">
    <div class="page-container">
      <div v-if="loading" class="loading-state">Chargement...</div>
      <template v-else>
        <div class="page-header">
          <h1>Modifier l'ordonnance #{{ route.params.id }}</h1>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="errors" class="alert alert-error">
          <div v-for="(msgs, field) in errors" :key="field">
            <strong>{{ field }}:</strong> {{ Array.isArray(msgs) ? msgs.join(', ') : msgs }}
          </div>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
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
                <input v-model="form.patient_phone" type="tel" required />
              </div>
              <div class="form-group">
                <label>Email</label>
                <input v-model="form.patient_email" type="email" required />
              </div>
            </div>
            <div class="form-card">
              <h3>Médecin</h3>
              <div class="doctor-display">
                <p><strong>Dr. {{ originalData?.doctor_name }}</strong></p>
                <p>{{ originalData?.doctor_specialisation }}</p>
              </div>
            </div>
          </div>

          <div class="form-card">
            <h3>Prescription</h3>
            <div class="form-group">
              <textarea v-model="form.medicaments" rows="5" required></textarea>
            </div>
          </div>

          <div class="form-card">
            <h3>Notes</h3>
            <div class="form-group">
              <textarea v-model="form.notes" rows="3"></textarea>
            </div>
          </div>

          <div class="form-actions">
            <router-link :to="`/doctor/ordonnance/${route.params.id}`" class="btn-cancel">Annuler</router-link>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getOrdonnance, updateOrdonnance } from "@/services/ordonnance";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const errors = ref(null);
const originalData = ref(null);

const form = reactive({
  patient_first_name: "", patient_last_name: "", patient_date_birth: "",
  patient_phone: "", patient_email: "", medicaments: "", notes: "",
});

onMounted(async () => {
  try {
    const data = await getOrdonnance(route.params.id);
    originalData.value = data;
    form.patient_first_name = data.patient_first_name;
    form.patient_last_name = data.patient_last_name;
    form.patient_date_birth = data.patient_date_birth;
    form.patient_phone = data.patient_phone;
    form.patient_email = data.patient_email;
    form.notes = data.notes;
    if (Array.isArray(data.medicaments)) {
      form.medicaments = data.medicaments.map(m => m.nom || String(m)).join(", ");
    } else {
      form.medicaments = data.medicaments || "";
    }
  } catch {
    error.value = "Impossible de charger l'ordonnance";
  } finally {
    loading.value = false;
  }
});

async function handleSubmit() {
  error.value = "";
  errors.value = null;
  saving.value = true;
  try {
    await updateOrdonnance(route.params.id, form);
    router.push(`/doctor/ordonnance/${route.params.id}`);
  } catch (err) {
    if (err.data?.errors) {
      errors.value = err.response.data.errors;
    } else {
      error.value = err.data?.error || "Erreur lors de la modification";
    }
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.page { padding: 2rem; }
.page-container { max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.5rem; color: #1a1a2e; }
.loading-state { text-align: center; padding: 3rem; color: #666; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
.form-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.25rem; }
.form-card h3 { font-size: 1rem; color: #1a1a2e; margin: 0 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { margin-bottom: 0.75rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.3rem; font-size: 0.85rem; }
.form-group input, .form-group textarea {
  width: 100%; padding: 0.65rem 0.8rem; border: 2px solid #e0e0e0; border-radius: 8px;
  font-size: 0.95rem; font-family: inherit; resize: vertical;
}
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #4e73df; }
.doctor-display { background: #f8f9fc; padding: 1rem; border-radius: 10px; }
.doctor-display p { margin: 0.15rem 0; font-size: 0.9rem; color: #666; }
.form-actions { display: flex; justify-content: space-between; margin-top: 1rem; }
.btn-cancel { padding: 0.75rem 1.5rem; background: #e9ecef; color: #495057; border-radius: 10px; text-decoration: none; font-weight: 600; }
.btn-submit { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #4e73df, #224abe); color: #fff; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.85rem; }
</style>
