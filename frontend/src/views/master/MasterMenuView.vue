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
          <h3>{{ menu.label }}</h3>
        </router-link>
      </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../../components/common/AppLayout.vue'

const masterMenus = [
  { path: '/master/customers', label: 'customer' },
  { path: '/master/products', label: 'product' },
  { path: '/master/employees', label: 'employee' },
  { path: '/master/suppliers', label: 'supplier' },
  { path: '/master/process-names', label: 'process name type' },
  { path: '/master/material-rates', label: 'material rate' },
  { path: '/master/machines', label: 'machine list' },
  { path: '/master/cycletimes', label: 'cycletime' },
  { path: '/master/holidays', label: 'holiday' },
]
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.master-menu-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.master-menu-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.master-menu-card h3 {
  color: var(--primary);
  margin: 0;
}
</style>
