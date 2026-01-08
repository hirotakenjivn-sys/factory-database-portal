<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material Specifications</h1>

    <!-- Registration Form -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>{{ editingId ? 'Edit Specification' : 'Register Specification' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end; margin-bottom: var(--spacing-md);">
          <div style="width: 200px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Material Type</label>
            <AutocompleteInput
              v-model="form.material_type_id"
              endpoint="/material/autocomplete/material-types"
              display-field="name"
              value-field="id"
              placeholder="Select Material Type..."
              required
            />
          </div>
          <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Form</label>
            <select v-model="form.material_form_code" class="form-input" required>
              <option :value="null">Select Form</option>
              <option v-for="f in materialForms" :key="f.material_form_code" :value="f.material_form_code">
                {{ f.form_name }}
              </option>
            </select>
          </div>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end; margin-bottom: var(--spacing-md);">
          <div style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Thickness (mm)</label>
            <input v-model.number="form.thickness_mm" class="form-input" type="number" step="0.001" />
          </div>
          <div style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Width (mm)</label>
            <input v-model.number="form.width_mm" class="form-input" type="number" step="0.01" />
          </div>
          <div style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Length (mm)</label>
            <input v-model.number="form.length_mm" class="form-input" type="number" step="0.01" />
          </div>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end; margin-bottom: var(--spacing-md);">
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Thick Tol +</label>
            <input v-model.number="form.thickness_tol_plus" class="form-input" type="number" step="0.0001" />
          </div>
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Thick Tol -</label>
            <input v-model.number="form.thickness_tol_minus" class="form-input" type="number" step="0.0001" />
          </div>
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Width Tol +</label>
            <input v-model.number="form.width_tol_plus" class="form-input" type="number" step="0.001" />
          </div>
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Width Tol -</label>
            <input v-model.number="form.width_tol_minus" class="form-input" type="number" step="0.001" />
          </div>
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Len Tol +</label>
            <input v-model.number="form.length_tol_plus" class="form-input" type="number" step="0.001" />
          </div>
          <div style="width: 90px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Len Tol -</label>
            <input v-model.number="form.length_tol_minus" class="form-input" type="number" step="0.001" />
          </div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button type="submit" class="btn btn-primary">
            {{ editingId ? 'Update' : 'Register' }}
          </button>
          <button v-if="editingId" type="button" class="btn btn-secondary" @click="cancelEdit">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- List -->
    <div class="card">
      <h2>Specification List</h2>
      <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
        <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
      </div>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Material</th>
              <th>Form</th>
              <th>Thickness</th>
              <th>Width</th>
              <th>Length</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in specs" :key="item.material_spec_id">
              <td>{{ item.material_spec_id }}</td>
              <td>{{ item.material_name }}</td>
              <td>{{ item.form_name }}</td>
              <td>{{ item.thickness_mm || '-' }}</td>
              <td>{{ item.width_mm || '-' }}</td>
              <td>{{ item.length_mm || '-' }}</td>
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleEdit(item)">Edit</button>
                  <button
                    v-if="editingId === item.material_spec_id"
                    class="btn btn-danger btn-sm"
                    @click="handleDelete(item.material_spec_id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="specs.length === 0" class="empty-state">
        <p>No specifications found</p>
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
  material_type_id: null,
  material_form_code: null,
  thickness_mm: null,
  width_mm: null,
  length_mm: null,
  thickness_tol_plus: null,
  thickness_tol_minus: null,
  width_tol_plus: null,
  width_tol_minus: null,
  length_tol_plus: null,
  length_tol_minus: null,
})
const editingId = ref(null)
const specs = ref([])
const materialForms = ref([])

const loadSpecs = async () => {
  try {
    const response = await api.get('/material/material-specs', { params: { limit: 100 } })
    specs.value = response.data
  } catch (error) {
    console.error('Failed to load specs:', error)
  }
}

const loadForms = async () => {
  try {
    const response = await api.get('/material/material-forms')
    materialForms.value = response.data
  } catch (error) {
    console.error('Failed to load forms:', error)
  }
}

const handleSubmit = async () => {
  try {
    if (editingId.value) {
      await api.put(`/material/material-specs/${editingId.value}`, form.value)
      alert('Specification updated successfully')
    } else {
      await api.post('/material/material-specs', form.value)
      alert('Specification registered successfully')
    }
    resetForm()
    await loadSpecs()
  } catch (error) {
    console.error('Failed to save spec:', error)
    const detail = error.response?.data?.detail || 'Failed to save specification'
    alert(detail)
  }
}

const handleEdit = (item) => {
  editingId.value = item.material_spec_id
  form.value = {
    material_type_id: item.material_type_id,
    material_form_code: item.material_form_code,
    thickness_mm: item.thickness_mm,
    width_mm: item.width_mm,
    length_mm: item.length_mm,
    thickness_tol_plus: item.thickness_tol_plus,
    thickness_tol_minus: item.thickness_tol_minus,
    width_tol_plus: item.width_tol_plus,
    width_tol_minus: item.width_tol_minus,
    length_tol_plus: item.length_tol_plus,
    length_tol_minus: item.length_tol_minus,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this specification?')) return
  try {
    await api.delete(`/material/material-specs/${id}`)
    alert('Specification deleted successfully')
    resetForm()
    await loadSpecs()
  } catch (error) {
    console.error('Failed to delete spec:', error)
    const detail = error.response?.data?.detail || 'Failed to delete specification'
    alert(detail)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  form.value = {
    material_type_id: null,
    material_form_code: null,
    thickness_mm: null,
    width_mm: null,
    length_mm: null,
    thickness_tol_plus: null,
    thickness_tol_minus: null,
    width_tol_plus: null,
    width_tol_minus: null,
    length_tol_plus: null,
    length_tol_minus: null,
  }
  editingId.value = null
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/material/material-specs', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['ID', 'Material', 'Form', 'Thickness', 'Width', 'Length']
    const rows = allData.map(s => [
      s.material_spec_id,
      `"${(s.material_name || '').replace(/"/g, '""')}"`,
      `"${(s.form_name || '').replace(/"/g, '""')}"`,
      s.thickness_mm || '',
      s.width_mm || '',
      s.length_mm || ''
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'material_specs.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadSpecs()
  loadForms()
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

.table-wrapper {
  overflow-x: auto;
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
