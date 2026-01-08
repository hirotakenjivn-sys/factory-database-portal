<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Current Material Stock</h1>

    <!-- Filters -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>Filters</h2>
      <div style="display: flex; gap: var(--spacing-sm); align-items: center; flex-wrap: wrap;">
        <select v-model="filterFactory" @change="loadStock" class="form-input" style="max-width: 180px;">
          <option :value="null">All Factories</option>
          <option v-for="f in factories" :key="f.factory_id" :value="f.factory_id">
            {{ f.factory_name }}
          </option>
        </select>
        <button class="btn btn-secondary" @click="loadStock">Refresh</button>
        <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
      </div>
    </div>

    <!-- Stock Table -->
    <div class="card">
      <h2>Stock List</h2>
      <table class="table">
        <thead>
          <tr>
            <th>LOT No</th>
            <th>Material Code</th>
            <th>Material</th>
            <th>Factory</th>
            <th>Supplier</th>
            <th>Sheet Qty</th>
            <th>Coil Qty</th>
            <th>Weight (kg)</th>
            <th>Last Updated</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in stock" :key="`${item.lot_id}-${item.factory_id}`">
            <td><strong>{{ item.lot_no }}</strong></td>
            <td>{{ item.material_code }}</td>
            <td>{{ item.material_name || '-' }}</td>
            <td>{{ item.factory_name }}</td>
            <td>{{ item.supplier_name || '-' }}</td>
            <td :class="{ 'negative': item.sheet_qty < 0 }">{{ item.sheet_qty || 0 }}</td>
            <td :class="{ 'negative': item.coil_qty < 0 }">{{ item.coil_qty || 0 }}</td>
            <td :class="{ 'negative': item.weight_kg < 0 }">{{ item.weight_kg || 0 }}</td>
            <td>{{ formatDate(item.last_updated) }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="stock.length === 0" class="empty-state">
        <p>No stock data found</p>
      </div>
    </div>

    <!-- Summary -->
    <div class="card" style="margin-top: var(--spacing-lg)">
      <h2>Stock Summary</h2>
      <div class="summary-grid">
        <div class="summary-item">
          <span class="summary-label">Total LOTs:</span>
          <span class="summary-value">{{ stock.length }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Sheets:</span>
          <span class="summary-value">{{ totalSheets }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Coils:</span>
          <span class="summary-value">{{ totalCoils }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Weight:</span>
          <span class="summary-value">{{ totalWeight.toFixed(3) }} kg</span>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const stock = ref([])
const factories = ref([])
const filterFactory = ref(null)

const totalSheets = computed(() => stock.value.reduce((sum, s) => sum + (s.sheet_qty || 0), 0))
const totalCoils = computed(() => stock.value.reduce((sum, s) => sum + (s.coil_qty || 0), 0))
const totalWeight = computed(() => stock.value.reduce((sum, s) => sum + parseFloat(s.weight_kg || 0), 0))

const loadStock = async () => {
  try {
    const params = {}
    if (filterFactory.value) params.factory_id = filterFactory.value
    const response = await api.get('/material/material-stock', { params })
    stock.value = response.data
  } catch (error) {
    console.error('Failed to load stock:', error)
    alert('Failed to load stock data')
  }
}

const loadFactories = async () => {
  try {
    const response = await api.get('/master/autocomplete/factories')
    factories.value = response.data.map(f => ({ factory_id: f.id, factory_name: f.name }))
  } catch (error) {
    console.error('Failed to load factories:', error)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ja-JP')
}

const downloadCSV = async () => {
  try {
    const params = {}
    if (filterFactory.value) params.factory_id = filterFactory.value
    const response = await api.get('/material/material-stock', { params })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['LOT No', 'Material Code', 'Material', 'Factory', 'Supplier', 'Sheet Qty', 'Coil Qty', 'Weight (kg)', 'Last Updated']
    const rows = allData.map(s => [
      `"${(s.lot_no || '').replace(/"/g, '""')}"`,
      `"${(s.material_code || '').replace(/"/g, '""')}"`,
      `"${(s.material_name || '').replace(/"/g, '""')}"`,
      `"${(s.factory_name || '').replace(/"/g, '""')}"`,
      `"${(s.supplier_name || '').replace(/"/g, '""')}"`,
      s.sheet_qty || 0,
      s.coil_qty || 0,
      s.weight_kg || 0,
      s.last_updated || ''
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'material_stock.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadStock()
  loadFactories()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.negative {
  color: var(--error);
  font-weight: bold;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  background: var(--background-secondary);
  border-radius: 4px;
}

.summary-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.summary-value {
  font-weight: bold;
  font-size: 1.1em;
}
</style>
