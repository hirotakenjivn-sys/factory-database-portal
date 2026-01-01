<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
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
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search Machine No..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
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
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
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
