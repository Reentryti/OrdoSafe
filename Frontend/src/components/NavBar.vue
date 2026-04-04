<template>
  <nav class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="navbar-brand">
        <span class="brand-icon">&#9764;</span>
        OrdoSafe
      </router-link>

      <div class="navbar-user" v-if="state.user">
        <span class="user-role-badge">{{ roleName }}</span>
        <span class="user-name">{{ state.user.full_name }}</span>
        <button class="btn-logout" @click="handleLogout">Déconnexion</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const { state, logout } = useAuthStore();

const roleName = computed(() => {
  const roles = { doctor: "Médecin", pharmacist: "Pharmacien", patient: "Patient" };
  return roles[state.user?.role] || "";
});

async function handleLogout() {
  await logout();
  router.push("/");
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  padding: 0 2rem;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}
.navbar-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.navbar-brand {
  color: #fff;
  font-size: 1.4rem;
  font-weight: 700;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.brand-icon {
  font-size: 1.6rem;
}
.navbar-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.user-name {
  color: #ccc;
  font-size: 0.9rem;
}
.user-role-badge {
  background: rgba(78, 115, 223, 0.3);
  color: #7c9df7;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}
.btn-logout {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.4rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.btn-logout:hover {
  background: rgba(244, 67, 54, 0.3);
  border-color: rgba(244, 67, 54, 0.5);
}
</style>
