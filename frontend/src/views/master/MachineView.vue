<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Machine List Master</h1>

      <!-- Tab Navigation -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'machines'"
          :class="{ active: activeTab === 'machines' }"
          class="tab-btn"
        >
          Machine List
        </button>
        <button
          @click="activeTab = 'machine-types'"
          :class="{ active: activeTab === 'machine-types' }"
          class="tab-btn"
        >
          Machine Type Management
        </button>
      </div>

      <!-- Machine List Tab -->
      <div v-if="activeTab === 'machines'">
      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editingMachineId ? 'Edit Machine' : 'Register Machine' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Machine No</label>
              <input v-model="form.machine_no" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Machine Type</label>
              <select v-model="form.machine_type_id" class="form-input" required>
                <option :value="null">Select Type</option>
                <option v-for="type in machineTypes" :key="type.machine_type_id" :value="type.machine_type_id">
                  {{ type.machine_type_name }}
                </option>
              </select>
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Factory Name</label>
              <AutocompleteInput
                v-model="form.factory_id"
                endpoint="/master/autocomplete/factories"
                display-field="name"
                value-field="id"
                placeholder="Enter Factory Name..."
                required
              />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">
                {{ editingMachineId ? 'Update' : 'Register' }}
              </button>
              <button v-if="editingMachineId" type="button" class="btn btn-secondary" @click="cancelMachineEdit">
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Machine List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Machine No..."
            style="max-width: 175px;"
          />
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Machine No</th>
              <th>Machine Type</th>
              <th>Factory Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in machines" :key="item.machine_list_id">
              <td>{{ item.machine_list_id }}</td>
              <td>{{ item.machine_no }}</td>
              <td>{{ item.machine_type_name || '-' }}</td>
              <td>{{ item.factory_name || '-' }}</td>
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleMachineEdit(item)">Edit</button>
                  <button
                    v-if="editingMachineId === item.machine_list_id"
                    class="btn btn-danger btn-sm"
                    @click="handleMachineDelete(item.machine_list_id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="machines.length === 0" class="empty-state">
          <p>No machine data found</p>
        </div>
      </div>
      </div>

      <!-- Machine Type Management Tab -->
      <div v-if="activeTab === 'machine-types'">
        <!-- Machine Type Registration Form -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>{{ editingMachineTypeId ? 'Edit Machine Type' : 'Register Machine Type' }}</h2>
          <form @submit.prevent="handleMachineTypeSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Machine Type Name</label>
              <input v-model="machineTypeForm.machine_type_name" class="form-input" type="text" required />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">
                {{ editingMachineTypeId ? 'Update' : 'Register' }}
              </button>
              <button v-if="editingMachineTypeId" type="button" class="btn btn-secondary" @click="cancelMachineTypeEdit">
                Cancel
              </button>
            </div>
          </form>
        </div>

        <!-- Machine Type List -->
        <div class="card">
          <h2>Machine Type List</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Machine Type Name</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="type in machineTypes" :key="type.machine_type_id">
                <td>{{ type.machine_type_id }}</td>
                <td>{{ type.machine_type_name }}</td>
                <td>
                  <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary btn-sm" @click="handleMachineTypeEdit(type)">Edit</button>
                    <button
                      v-if="editingMachineTypeId === type.machine_type_id"
                      class="btn btn-danger btn-sm"
                      @click="handleMachineTypeDelete(type.machine_type_id)"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="machineTypes.length === 0" class="empty-state">
            <p>No machine type data found</p>
          </div>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import api from '../../utils/api'

const activeTab = ref('machines')

// Machine form
const form = ref({
  machine_no: '',
  machine_type_id: null,
  factory_id: null,
})
const editingMachineId = ref(null)

// Machine Type form
const machineTypeForm = ref({
  machine_type_name: '',
})
const editingMachineTypeId = ref(null)

const machines = ref([])
const machineTypes = ref([])
const searchQuery = ref('')

const loadMachineTypes = async () => {
  try {
    const response = await api.get('/master/machine-types')
    machineTypes.value = response.data
  } catch (error) {
    console.error('Failed to load machine types:', error)
  }
}

const loadMachines = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/machines', { params })
    machines.value = response.data
  } catch (error) {
    console.error('Failed to load machines:', error)
    alert('Failed to load machines')
  }
}

// Machine CRUD
const handleSubmit = async () => {
  try {
    if (editingMachineId.value) {
      await api.put(`/master/machines/${editingMachineId.value}`, form.value)
      alert('Machine updated successfully')
    } else {
      await api.post('/master/machines', form.value)
      alert('Machine registered successfully')
    }
    resetMachineForm()
    await loadMachines()
  } catch (error) {
    console.error('Failed to save machine:', error)
    const detail = error.response?.data?.detail || 'Failed to save machine'
    alert(detail)
  }
}

const handleMachineEdit = (item) => {
  editingMachineId.value = item.machine_list_id
  form.value = {
    machine_no: item.machine_no,
    machine_type_id: item.machine_type_id,
    factory_id: item.factory_id,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleMachineDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this machine?')) return

  try {
    await api.delete(`/master/machines/${id}`)
    alert('Machine deleted successfully')
    resetMachineForm()
    await loadMachines()
  } catch (error) {
    console.error('Failed to delete machine:', error)
    const detail = error.response?.data?.detail || 'Failed to delete machine'
    alert(detail)
  }
}

const cancelMachineEdit = () => {
  resetMachineForm()
}

const resetMachineForm = () => {
  form.value = {
    machine_no: '',
    machine_type_id: null,
    factory_id: null,
  }
  editingMachineId.value = null
}

const handleSearch = () => {
  loadMachines(searchQuery.value)
}

// Machine Type CRUD
const handleMachineTypeSubmit = async () => {
  try {
    if (editingMachineTypeId.value) {
      await api.put(`/master/machine-types/${editingMachineTypeId.value}`, machineTypeForm.value)
      alert('Machine type updated successfully')
    } else {
      await api.post('/master/machine-types', machineTypeForm.value)
      alert('Machine type registered successfully')
    }
    resetMachineTypeForm()
    await loadMachineTypes()
  } catch (error) {
    console.error('Failed to save machine type:', error)
    const detail = error.response?.data?.detail || 'Failed to save machine type'
    alert(detail)
  }
}

const handleMachineTypeEdit = (type) => {
  editingMachineTypeId.value = type.machine_type_id
  machineTypeForm.value = {
    machine_type_name: type.machine_type_name,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleMachineTypeDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this machine type?')) return

  try {
    await api.delete(`/master/machine-types/${id}`)
    alert('Machine type deleted successfully')
    resetMachineTypeForm()
    await loadMachineTypes()
  } catch (error) {
    console.error('Failed to delete machine type:', error)
    const detail = error.response?.data?.detail || 'Failed to delete machine type'
    alert(detail)
  }
}

const cancelMachineTypeEdit = () => {
  resetMachineTypeForm()
}

const resetMachineTypeForm = () => {
  machineTypeForm.value = {
    machine_type_name: '',
  }
  editingMachineTypeId.value = null
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/master/machines', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['ID', 'Machine No', 'Machine Type', 'Factory Name']
    const rows = allData.map(m => [
      m.machine_list_id,
      `"${(m.machine_no || '').replace(/"/g, '""')}"`,
      `"${(m.machine_type_name || '').replace(/"/g, '""')}"`,
      `"${(m.factory_name || '').replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'machines.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadMachineTypes()
  loadMachines()
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
