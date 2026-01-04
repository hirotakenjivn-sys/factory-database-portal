<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Material Spec Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Material Spec</h2>
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
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Thickness</label>
              <input v-model.number="form.thickness" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Width</label>
              <input v-model.number="form.width" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Pitch</label>
              <input v-model.number="form.pitch" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">H (Height)</label>
              <input v-model.number="form.h" class="form-input" type="number" step="0.01" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Material Spec List</h2>
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
              <th>Thickness</th>
              <th>Width</th>
              <th>Pitch</th>
              <th>H</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in materialRates" :key="item.material_rate_id">
              <td>{{ item.material_rate_id }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.thickness }}</td>
              <td>{{ item.width }}</td>
              <td>{{ item.pitch }}</td>
              <td>{{ item.h }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="materialRates.length === 0" class="empty-state">
          <p>No material spec data found</p>
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
  thickness: null,
  width: null,
  pitch: null,
  h: null,
})

const materialRates = ref([])
const searchQuery = ref('')

const loadMaterialRates = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/material-rates', { params })
    materialRates.value = response.data
  } catch (error) {
    console.error('Failed to load material rates:', error)
    alert('Failed to load material rates')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('Please select a product')
    return
  }

  try {
    await api.post('/master/material-rates', form.value)
    alert('Material spec registered successfully')
    form.value = {
      product_id: null,
      thickness: null,
      width: null,
      pitch: null,
      h: null,
    }
    await loadMaterialRates()
  } catch (error) {
    console.error('Failed to create material rate:', error)
    alert('Failed to register material spec')
  }
}

const handleSearch = () => {
  loadMaterialRates(searchQuery.value)
}

const downloadCSV = () => {
  if (materialRates.value.length === 0) {
    alert('No data to download')
    return
  }
  const headers = ['ID', 'Product Code', 'Thickness', 'Width', 'Pitch', 'H']
  const rows = materialRates.value.map(m => [
    m.material_rate_id,
    `"${(m.product_code || '').replace(/"/g, '""')}"`,
    m.thickness,
    m.width,
    m.pitch,
    m.h
  ])
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'material_rates.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadMaterialRates()
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
