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
          <h3>{{ menu.label }}<template v-if="menu.key"> ({{ counts[menu.key] ?? '-' }})</template></h3>
        </router-link>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const masterMenus = [
  { path: '/master/customers', label: 'CUSTOMER', icon: '👥', key: 'customers' },
  { path: '/master/products', label: 'PRODUCT', icon: '🔩', key: 'products' },
  { path: '/master/employees', label: 'EMPLOYEE', icon: '👷', key: 'employees' },
  { path: '/master/suppliers', label: 'SUPPLIER', icon: '🚚', key: 'suppliers' },
  { path: '/master/process-names', label: 'PROCESS NAME TYPE', icon: '🔄', key: 'process_name_types' },
  { path: '/master/material-rates', label: 'MATERIAL RATE', icon: '📐', key: 'material_rates' },
  { path: '/master/machines', label: 'MACHINE LIST', icon: '🏭', key: 'machine_list' },
  { path: '/master/cycletimes', label: 'CYCLETIME', icon: '⏱️', key: 'cycletimes' },
  { path: '/master/holidays', label: 'HOLIDAY', icon: '📅', key: 'calendar' },
  { path: '/press', label: 'PROCESS', icon: '⚙️', key: 'processes' },
  // Material Management
  { path: '/master/material-types', label: 'MATERIAL TYPES', icon: '🧱', key: 'material_types' },
  { path: '/master/material-specs', label: 'MATERIAL SPECS', icon: '📋', key: 'material_specs' },
  { path: '/master/material-items', label: 'MATERIAL ITEMS', icon: '📦', key: 'material_items' },
  { path: '/master/material-lots', label: 'MATERIAL LOTS', icon: '🧾', key: 'material_lots' },
  { path: '/master/material-transactions', label: 'MATERIAL TRANSACTIONS', icon: '⬆️⬇️', key: 'material_transactions' },
  { path: '/master/material-stock', label: 'MATERIAL STOCK', icon: '📊', key: 'material_stock' },
  { path: '/master/material-trace', label: 'MATERIAL TRACE', icon: '🔍' },
]

const counts = ref({})

const loadCounts = async () => {
  try {
    const response = await api.get('/master/table-counts')
    counts.value = response.data
  } catch (error) {
    console.error('Failed to load table counts:', error)
  }
}

onMounted(() => {
  loadCounts()
})
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
