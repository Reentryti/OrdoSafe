<template>
  <div class="dashboard">
    <div class="dashboard-container">
      <div class="dash-header">
        <h1>Rechercher une ordonnance</h1>
        <p>Bienvenue, {{ state.user?.full_name }}</p>
      </div>

      <!-- Search type -->
      <div class="search-tabs">
        <button :class="{ active: searchType === 'info' }" @click="searchType = 'info'">
          Recherche par informations patient
        </button>
        <button :class="{ active: searchType === 'contact' }" @click="searchType = 'contact'">
          Recherche par contact + code
        </button>
      </div>

      <!-- Info search -->
      <div v-if="searchType === 'info'" class="search-card">
        <p>Recherchez par nom, prénom ou notes du patient.</p>
        <div class="search-row">
          <input v-model="infoQuery" type="text" placeholder="Nom, prénom, notes..." @keyup.enter="searchByInfo" />
          <button @click="searchByInfo" class="btn-search" :disabled="searching">Rechercher</button>
        </div>
      </div>

      <!-- Contact search -->
      <div v-if="searchType === 'contact'" class="search-card">
        <p>Recherchez avec l'email/téléphone du patient et son code d'accès.</p>
        <div class="search-row">
          <input v-model="contactQuery" type="text" placeholder="Email ou téléphone" />
          <input v-model="codeQuery" type="text" placeholder="Code d'accès" />
          <button @click="searchByContact" class="btn-search" :disabled="searching">Rechercher</button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="searching" class="loading-state">Recherche en cours...</div>

      <!-- Error -->
      <div v-if="searchError" class="alert alert-error">{{ searchError }}</div>

      <!-- Results -->
      <div v-if="results !== null && !searching">
        <h3 class="results-title">{{ results.length }} résultat(s)</h3>

        <div v-if="results.length === 0" class="empty-state">Aucune ordonnance trouvée.</div>

        <div v-else class="results-grid">
          <div v-for="o in results" :key="o.id" class="result-card">
            <div class="result-header">
              <span class="result-id">Ordonnance #{{ o.id }}</span>
              <span class="badge" :class="'badge-' + o.status">{{ statusText(o.status) }}</span>
            </div>
            <p><strong>Patient :</strong> {{ o.patient_name }}</p>
            <p><strong>Date :</strong> {{ o.date_creation }}</p>
            <div class="result-actions">
              <router-link :to="`/pharmacist/ordonnance/${o.id}`" class="btn-sm btn-view">Voir détails</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { searchOrdonnances } from "@/services/ordonnance";
import { useAuthStore } from "@/stores/auth";

const { state } = useAuthStore();
const searchType = ref("info");
const infoQuery = ref("");
const contactQuery = ref("");
const codeQuery = ref("");
const results = ref(null);
const searching = ref(false);
const searchError = ref("");

async function searchByInfo() {
  if (infoQuery.value.length < 2) {
    searchError.value = "Veuillez entrer au moins 2 caractères";
    return;
  }
  await doSearch({ type: "info", q: infoQuery.value });
}

async function searchByContact() {
  if (!contactQuery.value || !codeQuery.value) {
    searchError.value = "Veuillez remplir les deux champs";
    return;
  }
  await doSearch({ type: "contact", contact: contactQuery.value, code: codeQuery.value });
}

async function doSearch(params) {
  searching.value = true;
  searchError.value = "";
  results.value = null;
  try {
    const data = await searchOrdonnances(params);
    results.value = data.results;
  } catch (err) {
    searchError.value = err.data?.error || "Erreur lors de la recherche";
  } finally {
    searching.value = false;
  }
}

function statusText(s) {
  return { draft: "Brouillon", issued: "Émise", fulfilled: "Honorée", cancelled: "Annulée" }[s] || s;
}
</script>

<style scoped>
.dashboard { padding: 2rem; max-width: 1100px; margin: 0 auto; }
.dash-header { margin-bottom: 1.5rem; }
.dash-header h1 { font-size: 1.6rem; color: #1a1a2e; margin: 0; }
.dash-header p { color: #666; margin: 0.25rem 0 0; }
.search-tabs { display: flex; gap: 0.75rem; margin-bottom: 1.25rem; }
.search-tabs button {
  flex: 1; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 10px;
  background: #fff; font-weight: 600; cursor: pointer; font-size: 0.9rem; color: #666;
  transition: all 0.2s;
}
.search-tabs button.active { border-color: #1cc88a; color: #1cc88a; background: #f0fdf4; }
.search-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem; }
.search-card p { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }
.search-row { display: flex; gap: 0.75rem; }
.search-row input {
  flex: 1; padding: 0.65rem 0.8rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem;
}
.search-row input:focus { outline: none; border-color: #1cc88a; }
.btn-search {
  background: #1cc88a; color: #fff; border: none; padding: 0.65rem 1.25rem; border-radius: 8px;
  font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-search:disabled { opacity: 0.6; cursor: not-allowed; }
.loading-state { text-align: center; padding: 2rem; color: #666; }
.empty-state { text-align: center; padding: 2rem; color: #666; background: #fff; border-radius: 12px; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; }
.results-title { font-size: 1.1rem; color: #1a1a2e; margin-bottom: 1rem; }
.results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 768px) { .results-grid { grid-template-columns: 1fr; } .search-row { flex-direction: column; } }
.result-card { background: #fff; border-radius: 12px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.result-id { font-weight: 700; color: #1a1a2e; }
.result-card p { margin: 0.3rem 0; font-size: 0.9rem; color: #444; }
.result-actions { margin-top: 0.75rem; }
.btn-sm { padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; text-decoration: none; }
.btn-view { background: #e3f2fd; color: #1565c0; }
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-draft { background: #e9ecef; color: #6c757d; }
.badge-issued { background: #d4edda; color: #155724; }
.badge-fulfilled { background: #cce5ff; color: #004085; }
.badge-cancelled { background: #f8d7da; color: #721c24; }
</style>
