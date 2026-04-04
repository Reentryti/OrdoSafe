<template>
  <div id="app">
    <NavBar v-if="!isAuthPage" />
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import NavBar from "@/components/NavBar.vue";

const route = useRoute();
const { init } = useAuthStore();

const isAuthPage = computed(() => {
  const path = route.path;
  return (
    path === "/" ||
    path.startsWith("/login") ||
    path.startsWith("/signup") ||
    path.startsWith("/verify-2fa") ||
    path.startsWith("/setup-2fa")
  );
});

onMounted(() => {
  init();
});
</script>

<style>
@import "./assets/base.css";

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    sans-serif;
  background: #f0f2f5;
  min-height: 100vh;
}

#app {
  max-width: 100%;
  margin: 0;
  padding: 0;
}

main {
  min-height: calc(100vh - 64px);
}
</style>
