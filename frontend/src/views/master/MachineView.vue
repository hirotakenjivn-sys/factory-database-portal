<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Machine List Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Machine</h2>
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
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
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
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in machines" :key="item.machine_list_id">
              <td>{{ item.machine_list_id }}</td>
              <td>{{ item.machine_no }}</td>
              <td>{{ item.machine_type_name || '-' }}</td>
              <td>{{ item.factory_name || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="machines.length === 0" class="empty-state">
          <p>No machine data found</p>
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
  machine_no: '',
  machine_type_id: null,
  factory_id: null,
})

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

const handleSubmit = async () => {
  try {
    await api.post('/master/machines', form.value)
    alert('Machine registered successfully')
    form.value = {
      machine_no: '',
      machine_type_id: null,
      factory_id: null,
    }
    await loadMachines()
  } catch (error) {
    console.error('Failed to create machine:', error)
    alert('Failed to register machine')
  }
}

const handleSearch = () => {
  loadMachines(searchQuery.value)
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
</style>
