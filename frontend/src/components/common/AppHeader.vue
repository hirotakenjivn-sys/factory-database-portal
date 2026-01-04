<template>
  <header class="app-header">
    <div class="app-header-title" @click="goToDashboard">HIROTA PRECISION PORTAL</div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.app-header-title {
  cursor: pointer;
  transition: opacity 0.2s;
}

.app-header-title:hover {
  opacity: 0.8;
}
</style>
