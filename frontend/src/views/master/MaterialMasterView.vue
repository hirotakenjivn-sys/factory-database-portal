<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material Master</h1>

    <!-- Tab Navigation -->
    <div class="tabs" style="margin-bottom: var(--spacing-lg)">
      <button
        @click="activeTab = 'types'"
        :class="{ active: activeTab === 'types' }"
        class="tab-btn"
      >
        Material Types
      </button>
      <button
        @click="activeTab = 'forms'"
        :class="{ active: activeTab === 'forms' }"
        class="tab-btn"
      >
        Material Forms
      </button>
    </div>

    <!-- Material Types Tab -->
    <div v-if="activeTab === 'types'">
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editingTypeId ? 'Edit Material Type' : 'Register Material Type' }}</h2>
        <form @submit.prevent="handleTypeSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 200px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Material Name</label>
              <input v-model="typeForm.material_name" class="form-input" type="text" required placeholder="e.g., SUS304, SPCC" />
            </div>
            <div style="width: 300px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Note</label>
              <input v-model="typeForm.note" class="form-input" type="text" placeholder="Optional note..." />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">
                {{ editingTypeId ? 'Update' : 'Register' }}
              </button>
              <button v-if="editingTypeId" type="button" class="btn btn-secondary" @click="cancelTypeEdit">
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>

      <div class="card">
        <h2>Material Type List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
          <input
            v-model="typeSearch"
            @input="loadTypes"
            class="form-input"
            type="text"
            placeholder="Search Material Name..."
            style="max-width: 200px;"
          />
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Material Name</th>
              <th>Note</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in materialTypes" :key="item.material_type_id">
              <td>{{ item.material_type_id }}</td>
              <td>{{ item.material_name }}</td>
              <td>{{ item.note || '-' }}</td>
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleTypeEdit(item)">Edit</button>
                  <button
                    v-if="editingTypeId === item.material_type_id"
                    class="btn btn-danger btn-sm"
                    @click="handleTypeDelete(item.material_type_id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="materialTypes.length === 0" class="empty-state">
          <p>No material types found</p>
        </div>
      </div>
    </div>

    <!-- Material Forms Tab -->
    <div v-if="activeTab === 'forms'">
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editingFormId ? 'Edit Material Form' : 'Register Material Form' }}</h2>
        <form @submit.prevent="handleFormSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Form Code</label>
              <input v-model="formForm.material_form_code" class="form-input" type="text" required placeholder="e.g., COIL" />
            </div>
            <div style="width: 200px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Form Name</label>
              <input v-model="formForm.form_name" class="form-input" type="text" required placeholder="e.g., Coil" />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">
                {{ editingFormId ? 'Update' : 'Register' }}
              </button>
              <button v-if="editingFormId" type="button" class="btn btn-secondary" @click="cancelFormEdit">
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>

      <div class="card">
        <h2>Material Form List</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Form Code</th>
              <th>Form Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in materialForms" :key="item.material_form_id">
              <td>{{ item.material_form_id }}</td>
              <td>{{ item.material_form_code }}</td>
              <td>{{ item.form_name }}</td>
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleFormEdit(item)">Edit</button>
                  <button
                    v-if="editingFormId === item.material_form_id"
                    class="btn btn-danger btn-sm"
                    @click="handleFormDelete(item.material_form_id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="materialForms.length === 0" class="empty-state">
          <p>No material forms found</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const activeTab = ref('types')

// Material Type
const typeForm = ref({ material_name: '', note: '' })
const editingTypeId = ref(null)
const materialTypes = ref([])
const typeSearch = ref('')

// Material Form
const formForm = ref({ material_form_code: '', form_name: '' })
const editingFormId = ref(null)
const materialForms = ref([])

const loadTypes = async () => {
  try {
    const params = { limit: 100 }
    if (typeSearch.value) params.search = typeSearch.value
    const response = await api.get('/material/material-types', { params })
    materialTypes.value = response.data
  } catch (error) {
    console.error('Failed to load material types:', error)
  }
}

const loadForms = async () => {
  try {
    const response = await api.get('/material/material-forms')
    materialForms.value = response.data
  } catch (error) {
    console.error('Failed to load material forms:', error)
  }
}

const handleTypeSubmit = async () => {
  try {
    if (editingTypeId.value) {
      await api.put(`/material/material-types/${editingTypeId.value}`, typeForm.value)
      alert('Material type updated successfully')
    } else {
      await api.post('/material/material-types', typeForm.value)
      alert('Material type registered successfully')
    }
    resetTypeForm()
    await loadTypes()
  } catch (error) {
    console.error('Failed to save material type:', error)
    const detail = error.response?.data?.detail || 'Failed to save material type'
    alert(detail)
  }
}

const handleTypeEdit = (item) => {
  editingTypeId.value = item.material_type_id
  typeForm.value = { material_name: item.material_name, note: item.note || '' }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleTypeDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this material type?')) return
  try {
    await api.delete(`/material/material-types/${id}`)
    alert('Material type deleted successfully')
    resetTypeForm()
    await loadTypes()
  } catch (error) {
    console.error('Failed to delete material type:', error)
    const detail = error.response?.data?.detail || 'Failed to delete material type'
    alert(detail)
  }
}

const cancelTypeEdit = () => {
  resetTypeForm()
}

const resetTypeForm = () => {
  typeForm.value = { material_name: '', note: '' }
  editingTypeId.value = null
}

const handleFormSubmit = async () => {
  try {
    if (editingFormId.value) {
      await api.put(`/material/material-forms/${editingFormId.value}`, formForm.value)
      alert('Material form updated successfully')
    } else {
      await api.post('/material/material-forms', formForm.value)
      alert('Material form registered successfully')
    }
    resetFormForm()
    await loadForms()
  } catch (error) {
    console.error('Failed to save material form:', error)
    const detail = error.response?.data?.detail || 'Failed to save material form'
    alert(detail)
  }
}

const handleFormEdit = (item) => {
  editingFormId.value = item.material_form_id
  formForm.value = { material_form_code: item.material_form_code, form_name: item.form_name }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleFormDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this material form?')) return
  try {
    await api.delete(`/material/material-forms/${id}`)
    alert('Material form deleted successfully')
    resetFormForm()
    await loadForms()
  } catch (error) {
    console.error('Failed to delete material form:', error)
    const detail = error.response?.data?.detail || 'Failed to delete material form'
    alert(detail)
  }
}

const cancelFormEdit = () => {
  resetFormForm()
}

const resetFormForm = () => {
  formForm.value = { material_form_code: '', form_name: '' }
  editingFormId.value = null
}

onMounted(() => {
  loadTypes()
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

.tabs {
  display: flex;
  gap: var(--spacing-sm);
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  padding: var(--spacing-md) var(--spacing-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--background-hover);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
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
