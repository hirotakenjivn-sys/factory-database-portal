<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Supplier Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Supplier</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Supplier Name</label>
              <input v-model="form.supplier_name" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Business Type</label>
              <input v-model="form.supplier_business" class="form-input" type="text" />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Supplier List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Supplier..."
            style="max-width: 175px;"
          />
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Supplier ID</th>
              <th>Supplier Name</th>
              <th>Business Type</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="supplier in suppliers" :key="supplier.supplier_id">
              <td>{{ supplier.supplier_id }}</td>
              <td>{{ supplier.supplier_name }}</td>
              <td>{{ supplier.supplier_business || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="suppliers.length === 0" class="empty-state">
          <p>No supplier data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const form = ref({
  supplier_name: '',
  supplier_business: '',
})

const suppliers = ref([])
const searchQuery = ref('')

const loadSuppliers = async (search = '') => {
  try {
    const response = await api.get('/master/suppliers', {
      params: { search },
    })
    suppliers.value = response.data
  } catch (error) {
    console.error('Failed to load suppliers:', error)
    alert('Failed to load suppliers')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/suppliers', form.value)
    alert('Supplier registered successfully')
    form.value = {
      supplier_name: '',
      supplier_business: '',
    }
    await loadSuppliers()
  } catch (error) {
    console.error('Failed to create supplier:', error)
    alert('Failed to register supplier')
  }
}

const handleSearch = () => {
  loadSuppliers(searchQuery.value)
}

const downloadCSV = () => {
  if (suppliers.value.length === 0) {
    alert('No data to download')
    return
  }
  const headers = ['Supplier ID', 'Supplier Name', 'Business Type']
  const rows = suppliers.value.map(s => [
    s.supplier_id,
    `"${(s.supplier_name || '').replace(/"/g, '""')}"`,
    `"${(s.supplier_business || '').replace(/"/g, '""')}"`
  ])
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'suppliers.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadSuppliers()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
