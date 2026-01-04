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
          <p>{{ menu.description }}</p>
        </router-link>
      </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../../components/common/AppLayout.vue'

const masterMenus = [
  { path: '/master/customers', label: 'Customer Master', description: 'Manage customer information' },
  { path: '/master/products', label: 'Product Code Master', description: 'Manage product codes' },
  { path: '/master/employees', label: 'Employee Master', description: 'Manage employee information' },
  { path: '/master/suppliers', label: 'Supplier Master', description: 'Manage supplier information' },
  { path: '/master/process-names', label: 'Process Name Master', description: 'Manage process names and types' },
  { path: '/master/material-rates', label: 'Material Spec Master', description: 'Manage material specifications' },
  { path: '/master/machines', label: 'Machine List Master', description: 'Manage machine equipment' },
  { path: '/master/cycletimes', label: 'Cycletime Master', description: 'Manage cycletime settings' },
  { path: '/master/holidays', label: 'Holiday Master', description: 'Manage holidays' },
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
  margin-bottom: var(--spacing-sm);
}

.master-menu-card p {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
</style>
