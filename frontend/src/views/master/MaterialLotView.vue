<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material LOT Management</h1>

    <!-- Registration Form -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>{{ editingId ? 'Edit LOT' : 'Register LOT' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 180px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Material Code</label>
            <AutocompleteInput
              v-model="form.material_code"
              endpoint="/material/autocomplete/material-items"
              display-field="material_code"
              value-field="material_code"
              placeholder="Select Material..."
              required
            />
          </div>
          <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">LOT No</label>
            <input v-model="form.lot_no" class="form-input" type="text" required placeholder="e.g., LOT-2024-001" />
          </div>
          <div style="width: 180px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Supplier</label>
            <AutocompleteInput
              v-model="form.supplier_id"
              endpoint="/master/autocomplete/suppliers"
              display-field="name"
              value-field="id"
              placeholder="Select Supplier..."
            />
          </div>
          <div style="width: 140px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Received Date</label>
            <input v-model="form.received_date" class="form-input" type="date" />
          </div>
          <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Inspection</label>
            <select v-model="form.inspection_status" class="form-input">
              <option value="PENDING">PENDING</option>
              <option value="PASSED">PASSED</option>
              <option value="FAILED">FAILED</option>
            </select>
          </div>
          <div style="display: flex; gap: 8px;">
            <button type="submit" class="btn btn-primary">
              {{ editingId ? 'Update' : 'Register' }}
            </button>
            <button v-if="editingId" type="button" class="btn btn-secondary" @click="cancelEdit">
              Cancel
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- List -->
    <div class="card">
      <h2>LOT List</h2>
      <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search LOT No..."
          style="max-width: 200px;"
        />
        <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>LOT ID</th>
            <th>LOT No</th>
            <th>Material Code</th>
            <th>Material</th>
            <th>Supplier</th>
            <th>Received Date</th>
            <th>Inspection</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in lots" :key="lot.lot_id">
            <td>{{ lot.lot_id }}</td>
            <td><strong>{{ lot.lot_no }}</strong></td>
            <td>{{ lot.material_code }}</td>
            <td>{{ lot.material_name || '-' }}</td>
            <td>{{ lot.supplier_name || '-' }}</td>
            <td>{{ lot.received_date || '-' }}</td>
            <td>
              <span :class="'status-' + (lot.inspection_status || 'pending').toLowerCase()">
                {{ lot.inspection_status || 'PENDING' }}
              </span>
            </td>
            <td>
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-secondary btn-sm" @click="handleEdit(lot)">Edit</button>
                <button
                  v-if="editingId === lot.lot_id"
                  class="btn btn-danger btn-sm"
                  @click="handleDelete(lot.lot_id)"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="lots.length === 0" class="empty-state">
        <p>No LOTs found</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import api from '../../utils/api'

const form = ref({
  material_code: null,
  lot_no: '',
  supplier_id: null,
  received_date: null,
  inspection_status: 'PENDING',
})
const editingId = ref(null)
const lots = ref([])
const searchQuery = ref('')

const loadLots = async (search = '') => {
  try {
    const params = { limit: 100 }
    if (search) params.search = search
    const response = await api.get('/material/material-lots', { params })
    lots.value = response.data
  } catch (error) {
    console.error('Failed to load lots:', error)
  }
}

const handleSubmit = async () => {
  try {
    if (editingId.value) {
      await api.put(`/material/material-lots/${editingId.value}`, form.value)
      alert('LOT updated successfully')
    } else {
      await api.post('/material/material-lots', form.value)
      alert('LOT registered successfully')
    }
    resetForm()
    await loadLots()
  } catch (error) {
    console.error('Failed to save lot:', error)
    const detail = error.response?.data?.detail || 'Failed to save LOT'
    alert(detail)
  }
}

const handleEdit = (lot) => {
  editingId.value = lot.lot_id
  form.value = {
    material_code: lot.material_code,
    lot_no: lot.lot_no,
    supplier_id: lot.supplier_id,
    received_date: lot.received_date,
    inspection_status: lot.inspection_status || 'PENDING',
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this LOT?')) return
  try {
    await api.delete(`/material/material-lots/${id}`)
    alert('LOT deleted successfully')
    resetForm()
    await loadLots()
  } catch (error) {
    console.error('Failed to delete lot:', error)
    const detail = error.response?.data?.detail || 'Failed to delete LOT'
    alert(detail)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  form.value = {
    material_code: null,
    lot_no: '',
    supplier_id: null,
    received_date: null,
    inspection_status: 'PENDING',
  }
  editingId.value = null
}

const handleSearch = () => {
  loadLots(searchQuery.value)
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/material/material-lots', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['LOT ID', 'LOT No', 'Material Code', 'Material', 'Supplier', 'Received Date', 'Inspection Status']
    const rows = allData.map(l => [
      l.lot_id,
      `"${(l.lot_no || '').replace(/"/g, '""')}"`,
      `"${(l.material_code || '').replace(/"/g, '""')}"`,
      `"${(l.material_name || '').replace(/"/g, '""')}"`,
      `"${(l.supplier_name || '').replace(/"/g, '""')}"`,
      l.received_date || '',
      l.inspection_status || ''
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'material_lots.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadLots()
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

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.status-pending {
  background: #f39c12;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.status-passed {
  background: var(--success);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.status-failed {
  background: var(--error);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}
</style>
