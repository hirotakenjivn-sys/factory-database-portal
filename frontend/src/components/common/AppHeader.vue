<template>
  <header class="app-header">
    <div class="app-header-title" @click="goToTrace">HIROTA PRECISION PORTAL</div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToTrace = () => {
  router.push('/trace')
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
