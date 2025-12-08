<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

// アプリ起動時にトークンがあればユーザー情報を取得
onMounted(() => {
  if (authStore.token) {
    authStore.fetchUser()
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}
</style>
