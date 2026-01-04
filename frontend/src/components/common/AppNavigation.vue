<template>
  <nav class="app-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-toggle" @click="toggleSidebar">
      <span class="toggle-icon">{{ isCollapsed ? '>' : '<' }}</span>
    </div>

    <div class="sidebar-menu">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
        :title="item.label"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
      </router-link>
    </div>

    <div class="sidebar-footer">
      <div class="user-info" v-if="authStore.user">
        <span class="user-icon">👤</span>
        <span class="user-name" v-show="!isCollapsed">{{ authStore.user.username }}</span>
      </div>
      <button @click="handleLogout" class="logout-btn" :title="isCollapsed ? 'Logout' : ''">
        <span class="logout-icon">🚪</span>
        <span class="logout-label" v-show="!isCollapsed">Logout</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const isCollapsed = ref(false)

const navItems = [
  { name: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { name: 'trace', label: 'Trace', path: '/trace', icon: '🔍' },
  { name: 'outsource', label: 'Outsource', path: '/outsource', icon: '🏭' },
  { name: 'schedule', label: 'Schedule', path: '/schedule', icon: '📅' },
  { name: 'sales', label: 'Sales', path: '/sales', icon: '💰' },
  { name: 'warehouse', label: 'Warehouse', path: '/warehouse', icon: '📦' },
  { name: 'mold', label: 'Mold', path: '/mold', icon: '🔧' },
  { name: 'master', label: 'Master', path: '/master', icon: '⚡' },
]

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 親コンポーネントから参照できるように公開
defineExpose({
  isCollapsed
})
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 200px;
  background: #2c3e50;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
}

.app-sidebar.collapsed {
  width: 60px;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #34495e;
}

.toggle-icon {
  color: white;
  font-size: 16px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.toggle-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.2s;
  margin-bottom: 4px;
  white-space: nowrap;
}

.nav-item:hover {
  background-color: #34495e;
}

.nav-item.active {
  background-color: var(--primary);
  font-weight: bold;
}

.nav-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.nav-label {
  overflow: hidden;
}

.sidebar-footer {
  border-top: 1px solid #34495e;
  padding: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #bdc3c7;
  padding: 12px;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
}

.user-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  background: transparent;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.logout-btn:hover {
  background-color: rgba(231, 76, 60, 0.2);
}

.logout-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}
</style>
