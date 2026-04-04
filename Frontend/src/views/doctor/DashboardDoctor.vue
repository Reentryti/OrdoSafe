<template>
  <div class="dashboard">
    <div class="dashboard-container">
      <div class="dash-header">
        <div>
          <h1>Gestion des ordonnances</h1>
          <p>Bienvenue, Dr. {{ state.user?.full_name }}</p>
        </div>
        <router-link to="/doctor/ordonnance/create" class="btn-new">
          + Nouvelle ordonnance
        </router-link>
      </div>

      <!-- Filters -->
      <div class="filters-card">
        <select v-model="statusFilter">
          <option value="">Tous les statuts</option>
          <option value="draft">Brouillon</option>
          <option value="issued">Émise</option>
          <option value="fulfilled">Honorée</option>
          <option value="cancelled">Annulée</option>
        </select>
        <input v-model="searchQuery" type="text" placeholder="Rechercher par patient..." @keyup.enter="loadOrdonnances" />
        <button @click="loadOrdonnances" class="btn-filter">Filtrer</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">Chargement...</div>

      <!-- Empty -->
      <div v-else-if="ordonnances.length === 0" class="empty-state">
        <p>Aucune ordonnance trouvée</p>
        <router-link to="/doctor/ordonnance/create" class="btn-new-sm">Créer votre première ordonnance</router-link>
      </div>

      <!-- List -->
      <div v-else class="ordonnances-list">
        <div v-for="o in ordonnances" :key="o.id" class="ordonnance-item">
          <div class="ordo-info">
            <h4>{{ o.patient_name }}</h4>
            <span class="ordo-date">{{ formatDate(o.date_creation) }}</span>
            <span class="badge" :class="'badge-' + o.status">{{ statusText(o.status) }}</span>
          </div>
          <div class="ordo-actions">
            <router-link :to="`/doctor/ordonnance/${o.id}`" class="btn-sm btn-view">Voir</router-link>
            <router-link v-if="o.status === 'draft'" :to="`/doctor/ordonnance/${o.id}/edit`" class="btn-sm btn-edit">Modifier</router-link>
            <button v-if="o.status === 'draft'" @click="handleSign(o.id)" class="btn-sm btn-sign">Signer</button>
            <button v-if="o.status === 'draft'" @click="handleDelete(o.id)" class="btn-sm btn-delete">Supprimer</button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button v-for="p in totalPages" :key="p" @click="goToPage(p)" :class="{ active: p === page }" class="page-btn">{{ p }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { getOrdonnances, signOrdonnance, deleteOrdonnance } from "@/services/ordonnance";
import { useAuthStore } from "@/stores/auth";

const { state } = useAuthStore();
const ordonnances = ref([]);
const loading = ref(true);
const statusFilter = ref("");
const searchQuery = ref("");
const page = ref(1);
const total = ref(0);
const pageSize = 10;

const totalPages = computed(() => Math.ceil(total.value / pageSize));

onMounted(() => loadOrdonnances());

async function loadOrdonnances() {
  loading.value = true;
  try {
    const data = await getOrdonnances({
      status: statusFilter.value,
      search: searchQuery.value,
      page: page.value,
      page_size: pageSize,
    });
    ordonnances.value = data.results;
    total.value = data.count;
  } catch {
    ordonnances.value = [];
  } finally {
    loading.value = false;
  }
}

function goToPage(p) {
  page.value = p;
  loadOrdonnances();
}

async function handleSign(id) {
  if (!confirm("Signer cette ordonnance ? Cette action est irréversible.")) return;
  try {
    await signOrdonnance(id);
    loadOrdonnances();
  } catch (err) {
    alert(err.data?.error || "Erreur lors de la signature");
  }
}

async function handleDelete(id) {
  if (!confirm("Supprimer cette ordonnance ?")) return;
  try {
    await deleteOrdonnance(id);
    loadOrdonnances();
  } catch (err) {
    alert(err.data?.error || "Erreur lors de la suppression");
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric" });
}
function statusText(s) {
  return { draft: "Brouillon", issued: "Émise", fulfilled: "Honorée", cancelled: "Annulée" }[s] || s;
}
</script>

<style scoped>
.dashboard { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.dash-header h1 { font-size: 1.6rem; color: #1a1a2e; margin: 0; }
.dash-header p { color: #666; margin: 0.25rem 0 0; }
.btn-new {
  background: linear-gradient(135deg, #4e73df, #224abe); color: #fff; padding: 0.75rem 1.5rem;
  border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.95rem;
}
.btn-new:hover { opacity: 0.9; }
.filters-card {
  display: flex; gap: 0.75rem; background: #fff; padding: 1rem; border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;
}
.filters-card select, .filters-card input {
  flex: 1; padding: 0.6rem 0.8rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.9rem;
}
.filters-card select:focus, .filters-card input:focus { outline: none; border-color: #4e73df; }
.btn-filter {
  background: #4e73df; color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 8px;
  font-weight: 600; cursor: pointer;
}
.loading-state, .empty-state { text-align: center; padding: 3rem; color: #666; }
.btn-new-sm {
  display: inline-block; margin-top: 1rem; background: #4e73df; color: #fff; padding: 0.6rem 1.2rem;
  border-radius: 8px; text-decoration: none; font-weight: 600;
}
.ordonnances-list { display: flex; flex-direction: column; gap: 0.75rem; }
.ordonnance-item {
  background: #fff; border-radius: 12px; padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex;
  justify-content: space-between; align-items: center;
}
.ordo-info h4 { margin: 0 0 0.25rem; color: #1a1a2e; }
.ordo-date { font-size: 0.85rem; color: #999; margin-right: 0.75rem; }
.badge {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px;
  font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
}
.badge-draft { background: #e9ecef; color: #6c757d; }
.badge-issued { background: #d4edda; color: #155724; }
.badge-fulfilled { background: #cce5ff; color: #004085; }
.badge-cancelled { background: #f8d7da; color: #721c24; }
.ordo-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.btn-sm {
  padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600;
  cursor: pointer; border: none; text-decoration: none; transition: opacity 0.2s;
}
.btn-view { background: #e3f2fd; color: #1565c0; }
.btn-edit { background: #fff3e0; color: #e65100; }
.btn-sign { background: #e8f5e9; color: #2e7d32; }
.btn-delete { background: #fce4ec; color: #c62828; }
.btn-sm:hover { opacity: 0.8; }
.pagination { display: flex; justify-content: center; gap: 0.5rem; margin-top: 1.5rem; }
.page-btn {
  width: 36px; height: 36px; border-radius: 8px; border: 2px solid #e0e0e0;
  background: #fff; cursor: pointer; font-weight: 600;
}
.page-btn.active { background: #4e73df; color: #fff; border-color: #4e73df; }
@media (max-width: 768px) {
  .ordonnance-item { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .filters-card { flex-direction: column; }
  .dash-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
}
</style>
