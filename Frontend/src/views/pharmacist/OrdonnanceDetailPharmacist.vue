<template>
  <div class="page">
    <div class="page-container">
      <div v-if="loading" class="loading-state">Chargement...</div>
      <div v-else-if="!ordonnance" class="empty-state">Ordonnance introuvable</div>
      <template v-else>
        <div class="detail-header">
          <div>
            <h1>Ordonnance #{{ ordonnance.id }}</h1>
            <span class="badge" :class="'badge-' + ordonnance.status">{{ statusText(ordonnance.status) }}</span>
          </div>
          <router-link to="/pharmacist/dashboard" class="btn-back">Retour</router-link>
        </div>

        <div class="detail-grid">
          <!-- Patient -->
          <div class="detail-card">
            <h3>Patient</h3>
            <div class="info-row"><span>Nom</span><strong>{{ ordonnance.patient_first_name }} {{ ordonnance.patient_last_name }}</strong></div>
            <div class="info-row"><span>Date de naissance</span><strong>{{ ordonnance.patient_date_birth }}</strong></div>
            <div class="info-row"><span>Téléphone</span><strong>{{ ordonnance.patient_phone || 'Non renseigné' }}</strong></div>
            <div class="info-row"><span>Email</span><strong>{{ ordonnance.patient_email || 'Non renseigné' }}</strong></div>
            <div class="info-row"><span>Code d'accès</span><strong class="access-code">{{ ordonnance.access_code }}</strong></div>
          </div>

          <!-- Doctor -->
          <div class="detail-card">
            <h3>Médecin Prescripteur</h3>
            <div class="info-row"><span>Nom</span><strong>Dr. {{ ordonnance.doctor_name }}</strong></div>
            <div class="info-row"><span>Spécialité</span><strong>{{ ordonnance.doctor_specialisation }}</strong></div>
            <div class="info-row"><span>Date</span><strong>{{ formatDate(ordonnance.date_creation) }}</strong></div>
            <div class="info-row" v-if="ordonnance.has_signature">
              <span>Signature</span>
              <strong :class="ordonnance.signature_valid ? 'text-success' : 'text-danger'">
                {{ ordonnance.signature_valid ? 'Valide' : 'Invalide' }}
              </strong>
            </div>
          </div>
        </div>

        <!-- Medications -->
        <div class="detail-card">
          <h3>Prescription</h3>
          <div v-if="Array.isArray(ordonnance.medicaments)" class="meds-list">
            <div v-for="(med, i) in ordonnance.medicaments" :key="i" class="med-item">
              <strong>{{ med.nom || med }}</strong>
              <span v-if="med.posologie"> - {{ med.posologie }}</span>
              <span v-if="med.duree"> - {{ med.duree }}</span>
            </div>
          </div>
          <p v-else>{{ ordonnance.medicaments }}</p>
        </div>

        <!-- Notes -->
        <div v-if="ordonnance.notes" class="detail-card">
          <h3>Notes</h3>
          <p class="notes-text">{{ ordonnance.notes }}</p>
        </div>

        <!-- Actions -->
        <div class="pharmacist-actions">
          <button v-if="ordonnance.status === 'issued'" @click="handleValidate" class="btn-validate" :disabled="acting">
            Honorer l'ordonnance
          </button>
          <button v-if="ordonnance.status === 'issued'" @click="showReportModal = true" class="btn-report">
            Signaler
          </button>
          <button v-if="ordonnance.status !== 'fulfilled' && ordonnance.status !== 'cancelled'" @click="handleBlock" class="btn-block">
            Bloquer
          </button>
        </div>

        <!-- Report modal -->
        <div v-if="showReportModal" class="modal-overlay" @click.self="showReportModal = false">
          <div class="modal-card">
            <h3>Signaler cette ordonnance</h3>
            <div class="form-group">
              <label>Raison du signalement</label>
              <textarea v-model="reportReason" rows="3" placeholder="Décrivez la raison..."></textarea>
            </div>
            <div class="modal-actions">
              <button @click="showReportModal = false" class="btn-cancel-modal">Annuler</button>
              <button @click="handleReport" class="btn-confirm-report" :disabled="!reportReason || acting">Signaler</button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getPharmacistOrdonnance, validateOrdonnance, reportOrdonnance, blockOrdonnance } from "@/services/ordonnance";

const route = useRoute();
const router = useRouter();
const ordonnance = ref(null);
const loading = ref(true);
const acting = ref(false);
const showReportModal = ref(false);
const reportReason = ref("");

onMounted(async () => {
  try {
    ordonnance.value = await getPharmacistOrdonnance(route.params.id);
  } catch {
    ordonnance.value = null;
  } finally {
    loading.value = false;
  }
});

async function handleValidate() {
  if (!confirm("Confirmer l'honoration de cette ordonnance ?")) return;
  acting.value = true;
  try {
    await validateOrdonnance(ordonnance.value.id);
    ordonnance.value = await getPharmacistOrdonnance(route.params.id);
  } catch (err) {
    alert(err.data?.error || "Erreur");
  } finally {
    acting.value = false;
  }
}

async function handleReport() {
  acting.value = true;
  try {
    await reportOrdonnance(ordonnance.value.id, reportReason.value);
    showReportModal.value = false;
    ordonnance.value = await getPharmacistOrdonnance(route.params.id);
  } catch (err) {
    alert(err.data?.error || "Erreur");
  } finally {
    acting.value = false;
  }
}

async function handleBlock() {
  if (!confirm("Bloquer cette ordonnance ?")) return;
  acting.value = true;
  try {
    await blockOrdonnance(ordonnance.value.id);
    ordonnance.value = await getPharmacistOrdonnance(route.params.id);
  } catch (err) {
    alert(err.data?.error || "Erreur");
  } finally {
    acting.value = false;
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
function statusText(s) {
  return { draft: "Brouillon", issued: "Émise", fulfilled: "Honorée", cancelled: "Annulée" }[s] || s;
}
</script>

<style scoped>
.page { padding: 2rem; }
.page-container { max-width: 900px; margin: 0 auto; }
.loading-state, .empty-state { text-align: center; padding: 3rem; color: #666; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.detail-header h1 { font-size: 1.5rem; color: #1a1a2e; margin: 0 0 0.25rem; }
.btn-back { background: #e9ecef; color: #495057; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }
@media (max-width: 768px) { .detail-grid { grid-template-columns: 1fr; } }
.detail-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.25rem; }
.detail-card h3 { font-size: 1rem; color: #1cc88a; margin: 0 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee; }
.info-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f5f5f5; }
.info-row span { color: #666; font-size: 0.9rem; }
.info-row strong { font-size: 0.9rem; }
.access-code { background: #e3f2fd; color: #1565c0; padding: 0.15rem 0.5rem; border-radius: 6px; font-family: monospace; }
.text-success { color: #2e7d32; }
.text-danger { color: #c62828; }
.meds-list { display: flex; flex-direction: column; gap: 0.5rem; }
.med-item { background: #f8f9fc; padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.9rem; }
.notes-text { white-space: pre-line; color: #444; line-height: 1.6; }
.badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
.badge-draft { background: #e9ecef; color: #6c757d; }
.badge-issued { background: #d4edda; color: #155724; }
.badge-fulfilled { background: #cce5ff; color: #004085; }
.badge-cancelled { background: #f8d7da; color: #721c24; }
.pharmacist-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.btn-validate { background: #1cc88a; color: #fff; border: none; padding: 0.7rem 1.5rem; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.95rem; }
.btn-report { background: #fff3e0; color: #e65100; border: none; padding: 0.7rem 1.5rem; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-block { background: #fce4ec; color: #c62828; border: none; padding: 0.7rem 1.5rem; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-validate:disabled { opacity: 0.6; cursor: not-allowed; }
/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { background: #fff; border-radius: 16px; padding: 2rem; max-width: 460px; width: 90%; }
.modal-card h3 { margin: 0 0 1rem; color: #1a1a2e; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; color: #333; margin-bottom: 0.3rem; font-size: 0.9rem; }
.form-group textarea { width: 100%; padding: 0.65rem 0.8rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; resize: vertical; font-family: inherit; }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.btn-cancel-modal { background: #e9ecef; color: #495057; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-confirm-report { background: #e65100; color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-confirm-report:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
