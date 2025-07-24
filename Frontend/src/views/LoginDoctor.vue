<!-- src/views/Login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="w-full max-w-md p-6 bg-white rounded shadow">
      <h2 class="text-2xl font-bold text-center mb-6">Connexion</h2>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700">Nom d'utilisateur</label>
          <input v-model="username" type="text" class="w-full p-2 border rounded" required />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700">Mot de passe</label>
          <input v-model="password" type="password" class="w-full p-2 border rounded" required />
        </div>

        <div v-if="error" class="mb-4 text-red-500 text-sm">
          {{ error }}
        </div>

        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Se connecter
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useLogin } from "@/composables/useLogin";
const { username, password, role, error, handleLogin } = useLogin();
</script>
