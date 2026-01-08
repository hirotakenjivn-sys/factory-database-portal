<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material Items (Ledger)</h1>

    <!-- Registration Form -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>{{ editingCode ? 'Edit Material Item' : 'Register Material Item' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Material Code</label>
            <input v-model="form.material_code" class="form-input" type="text" required :disabled="!!editingCode" />
          </div>
          <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Spec ID</label>
            <select v-model="form.material_spec_id" class="form-input" required>
              <option :value="null">Select Spec</option>
              <option v-for="s in specs" :key="s.material_spec_id" :value="s.material_spec_id">
                {{ s.material_name }} - {{ s.form_name }} {{ s.thickness_mm ? `t${s.thickness_mm}` : '' }}
              </option>
            </select>
          </div>
          <div style="width: 250px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Description</label>
            <input v-model="form.description" class="form-input" type="text" placeholder="Optional description..." />
          </div>
          <div style="display: flex; gap: 8px;">
            <button type="submit" class="btn btn-primary">
              {{ editingCode ? 'Update' : 'Register' }}
            </button>
            <button v-if="editingCode" type="button" class="btn btn-secondary" @click="cancelEdit">
              Cancel
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- List -->
    <div class="card">
      <h2>Material Item List</h2>
      <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search Material Code..."
          style="max-width: 200px;"
        />
        <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Material Code</th>
            <th>Material Name</th>
            <th>Form</th>
            <th>Thickness</th>
            <th>Width</th>
            <th>Length</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.material_code">
            <td><strong>{{ item.material_code }}</strong></td>
            <td>{{ item.material_name || '-' }}</td>
            <td>{{ item.form_name || '-' }}</td>
            <td>{{ item.thickness_mm || '-' }}</td>
            <td>{{ item.width_mm || '-' }}</td>
            <td>{{ item.length_mm || '-' }}</td>
            <td>{{ item.description || '-' }}</td>
            <td>
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-secondary btn-sm" @click="handleEdit(item)">Edit</button>
                <button
                  v-if="editingCode === item.material_code"
                  class="btn btn-danger btn-sm"
                  @click="handleDelete(item.material_code)"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="items.length === 0" class="empty-state">
        <p>No material items found</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const form = ref({
  material_code: '',
  material_spec_id: null,
  description: '',
})
const editingCode = ref(null)
const items = ref([])
const specs = ref([])
const searchQuery = ref('')

const loadItems = async (search = '') => {
  try {
    const params = { limit: 100 }
    if (search) params.search = search
    const response = await api.get('/material/material-items', { params })
    items.value = response.data
  } catch (error) {
    console.error('Failed to load items:', error)
  }
}

const loadSpecs = async () => {
  try {
    const response = await api.get('/material/material-specs', { params: { limit: 1000 } })
    specs.value = response.data
  } catch (error) {
    console.error('Failed to load specs:', error)
  }
}

const handleSubmit = async () => {
  try {
    if (editingCode.value) {
      await api.put(`/material/material-items/${editingCode.value}`, form.value)
      alert('Material item updated successfully')
    } else {
      await api.post('/material/material-items', form.value)
      alert('Material item registered successfully')
    }
    resetForm()
    await loadItems()
  } catch (error) {
    console.error('Failed to save item:', error)
    const detail = error.response?.data?.detail || 'Failed to save material item'
    alert(detail)
  }
}

const handleEdit = (item) => {
  editingCode.value = item.material_code
  form.value = {
    material_code: item.material_code,
    material_spec_id: item.material_spec_id,
    description: item.description || '',
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (code) => {
  if (!confirm('Are you sure you want to delete this material item?')) return
  try {
    await api.delete(`/material/material-items/${code}`)
    alert('Material item deleted successfully')
    resetForm()
    await loadItems()
  } catch (error) {
    console.error('Failed to delete item:', error)
    const detail = error.response?.data?.detail || 'Failed to delete material item'
    alert(detail)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  form.value = {
    material_code: '',
    material_spec_id: null,
    description: '',
  }
  editingCode.value = null
}

const handleSearch = () => {
  loadItems(searchQuery.value)
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/material/material-items', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['Material Code', 'Material Name', 'Form', 'Thickness', 'Width', 'Length', 'Description']
    const rows = allData.map(i => [
      `"${(i.material_code || '').replace(/"/g, '""')}"`,
      `"${(i.material_name || '').replace(/"/g, '""')}"`,
      `"${(i.form_name || '').replace(/"/g, '""')}"`,
      i.thickness_mm || '',
      i.width_mm || '',
      i.length_mm || '',
      `"${(i.description || '').replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'material_items.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadItems()
  loadSpecs()
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
</style>
