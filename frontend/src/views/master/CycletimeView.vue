<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Cycletime Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Cycletime Setting</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Product Code</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="product_code"
                value-field="id"
                placeholder="Enter Product Code..."
                @select="handleProductSelect"
                required
              />
            </div>
            <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Process Name</label>
              <select v-model="form.process_name" class="form-input" required :disabled="!form.product_id">
                <option value="">Select Process</option>
                <option v-for="process in productProcesses" :key="process.process_id" :value="process.process_name">
                  {{ process.process_name }}
                </option>
              </select>
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
        <h2>Cycletime Setting List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Product Code..."
            style="max-width: 175px;"
          />
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
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
            <tr v-for="item in cycletimeSettings" :key="item.cycletime_id">
              <td>{{ item.cycletime_id }}</td>
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
        <div v-if="cycletimeSettings.length === 0" class="empty-state">
          <p>No cycletime setting data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import CopyableText from '../../components/common/CopyableText.vue'
import api from '../../utils/api'

const form = ref({
  product_id: null,
  process_name: '',
  press_no: '',
  cycle_time: null,
})

const cycletimeSettings = ref([])
const productProcesses = ref([])
const searchQuery = ref('')

const loadCycletimeSettings = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/cycletimes', { params })
    cycletimeSettings.value = response.data
  } catch (error) {
    console.error('Failed to load cycletime settings:', error)
    alert('Failed to load cycletime settings')
  }
}

const handleProductSelect = async (item) => {
  // Reset process name when product changes
  form.value.process_name = ''
  productProcesses.value = []

  if (!item || !item.id) return

  try {
    // Load process names for the selected product
    const response = await api.get(`/master/product/${item.id}/process-names`)
    productProcesses.value = response.data
  } catch (error) {
    console.error('Failed to load product processes:', error)
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('Please select a product')
    return
  }

  try {
    await api.post('/master/cycletimes', form.value)
    alert('Cycletime setting registered successfully')
    form.value = {
      product_id: null,
      process_name: '',
      press_no: '',
      cycle_time: null,
    }
    productProcesses.value = []
    await loadCycletimeSettings()
  } catch (error) {
    console.error('Failed to create cycletime settings:', error)
    alert('Failed to register cycletime setting')
  }
}

const handleSearch = () => {
  loadCycletimeSettings(searchQuery.value)
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/master/cycletimes', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['ID', 'Product Code', 'Process Name', 'Press No', 'Cycle Time']
    const rows = allData.map(c => [
      c.cycletime_id,
      `"${(c.product_code || '').replace(/"/g, '""')}"`,
      `"${(c.process_name || '').replace(/"/g, '""')}"`,
      `"${(c.press_no || '').replace(/"/g, '""')}"`,
      c.cycle_time
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'cycletimes.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadCycletimeSettings()
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
