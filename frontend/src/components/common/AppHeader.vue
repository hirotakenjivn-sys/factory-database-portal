<template>
  <header class="app-header">
    <div class="app-header-title" @click="goToTrace">HIROTA PRECISION PORTAL</div>
    <div v-if="authStore.user" class="user-menu-container">
      <button @click="toggleMenu" class="user-menu-button">
        <span>{{ authStore.user.username }}</span>
        <span class="dropdown-icon">▼</span>
      </button>
      <div v-if="isMenuOpen" class="user-dropdown-menu">
        <button @click="handleLogout" class="dropdown-item">
          ログアウト
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleLogout = () => {
  isMenuOpen.value = false
  authStore.logout()
  router.push('/login')
}

const goToTrace = () => {
  router.push('/trace')
}

// メニュー外をクリックしたら閉じる
const closeMenuOnClickOutside = (event) => {
  const menuContainer = document.querySelector('.user-menu-container')
  if (menuContainer && !menuContainer.contains(event.target)) {
    isMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeMenuOnClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenuOnClickOutside)
})
</script>

<style scoped>
.app-header-title {
  cursor: pointer;
  transition: opacity 0.2s;
}

.app-header-title:hover {
  opacity: 0.8;
}

.user-menu-container {
  position: relative;
}

.user-menu-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: white;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.2s;
}

.user-menu-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dropdown-icon {
  font-size: 10px;
  transition: transform 0.2s;
}

.user-menu-button:hover .dropdown-icon {
  transform: translateY(2px);
}

.user-dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  z-index: 1001;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  background: white;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: var(--background-hover);
}

.dropdown-item:active {
  background-color: var(--border);
}
</style>
