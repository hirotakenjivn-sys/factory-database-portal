<template>
  <AppLayout>
      <h1 class="page-title">Master Data Management</h1>

      <div class="grid grid-auto">
        <router-link
          v-for="menu in masterMenus"
          :key="menu.path"
          :to="menu.path"
          class="card master-menu-card"
        >
          <span class="menu-icon">{{ menu.icon }}</span>
          <h3>{{ menu.label }}</h3>
        </router-link>
      </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../../components/common/AppLayout.vue'

const masterMenus = [
  { path: '/master/customers', label: 'CUSTOMER', icon: '👥' },
  { path: '/master/products', label: 'PRODUCT', icon: '📦' },
  { path: '/master/employees', label: 'EMPLOYEE', icon: '👷' },
  { path: '/master/suppliers', label: 'SUPPLIER', icon: '🚚' },
  { path: '/master/process-names', label: 'PROCESS NAME TYPE', icon: '🔄' },
  { path: '/master/material-rates', label: 'MATERIAL RATE', icon: '📐' },
  { path: '/master/machines', label: 'MACHINE LIST', icon: '🏭' },
  { path: '/master/cycletimes', label: 'CYCLETIME', icon: '⏱️' },
  { path: '/master/holidays', label: 'HOLIDAY', icon: '📅' },
  { path: '/press', label: 'PRESS', icon: '⚙️' },
]
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.master-menu-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.master-menu-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.menu-icon {
  font-size: 24px;
}

.master-menu-card h3 {
  color: var(--primary);
  margin: 0;
}
</style>
