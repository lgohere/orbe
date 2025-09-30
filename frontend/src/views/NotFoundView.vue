<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 class="text-6xl font-bold text-orbe-white-accent mb-4">404</h1>
        <h2 class="text-2xl font-bold text-orbe-white-text-primary dark:text-orbe-black-text-primary mb-4">
          Página não encontrada
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          A página que você está procurando não existe.
        </p>

        <router-link
          to="/"
          class="btn btn-primary"
        >
          Ir para Início
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404 page component
</script>