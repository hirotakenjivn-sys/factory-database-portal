<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">SPM Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register SPM Setting</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Product Code</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="code"
                value-field="id"
                placeholder="Enter Product Code..."
                required
              />
            </div>
            <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Process Name</label>
              <AutocompleteInput
                v-model="form.process_name"
                endpoint="/master/autocomplete/process-names"
                display-field="name"
                value-field="name"
                placeholder="Enter Process Name..."
                required
              />
            </div>
            <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Press No</label>
              <AutocompleteInput
                v-model="form.press_no"
                endpoint="/master/autocomplete/machines"
                display-field="machine_no"
                value-field="machine_no"
                placeholder="Enter Press No..."
                :filter-params="{ machine_type: 'PRESS' }"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Cycle Time</label>
              <input v-model.number="form.cycle_time" class="form-input" type="number" step="0.01" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>SPM Setting List</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search Product Code..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product Code</th>
              <th>Process Name</th>
              <th>Press No</th>
              <th>Cycle Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in spmSettings" :key="item.spm_id">
              <td>{{ item.spm_id }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.process_name }}</td>
              <td>{{ item.press_no }}</td>
              <td>{{ item.cycle_time }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="spmSettings.length === 0" class="empty-state">
          <p>No SPM setting data found</p>
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
import CopyableText from '../../components/common/CopyableText.vue'
import api from '../../utils/api'

const form = ref({
  product_id: null,
  process_name: '',
  press_no: '',
  cycle_time: null,
})

const spmSettings = ref([])
const searchQuery = ref('')

const loadSpmSettings = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/spm', { params })
    spmSettings.value = response.data
  } catch (error) {
    console.error('Failed to load SPM settings:', error)
    alert('Failed to load SPM settings')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('Please select a product')
    return
  }

  try {
    await api.post('/master/spm', form.value)
    alert('SPM setting registered successfully')
    form.value = {
      product_id: null,
      process_name: '',
      press_no: '',
      cycle_time: null,
    }
    await loadSpmSettings()
  } catch (error) {
    console.error('Failed to create SPM settings:', error)
    alert('Failed to register SPM setting')
  }
}

const handleSearch = () => {
  loadSpmSettings(searchQuery.value)
}

onMounted(() => {
  loadSpmSettings()
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
