<template>
  <AppLayout>
      <h1 class="page-title">Warehouse - Finished Products</h1>

      <!-- Finished Product Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Finished Product</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Product Code</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="code"
                value-field="id"
                placeholder="Enter product code..."
                required
              />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Lot Number</label>
              <AutocompleteInput
                v-model="form.lot_id"
                endpoint="/master/autocomplete/lots"
                display-field="number"
                value-field="id"
                placeholder="Enter lot number..."
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Quantity</label>
              <input v-model.number="form.finished_quantity" class="form-input" type="number" required />
            </div>
            <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Finish Date</label>
              <input v-model="form.date_finished" class="form-input" type="text" placeholder="DD/MM/YYYY" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- Finished Products List -->
      <div class="card">
        <h2>Finished Products List</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Customer</th>
              <th>Product Code</th>
              <th>Lot Number</th>
              <th>Quantity</th>
              <th>Finish Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in finishedProducts" :key="item.finished_product_id">
              <td>{{ item.finished_product_id }}</td>
              <td>{{ item.customer_name || '-' }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.lot_number || '-' }}</td>
              <td>{{ item.finished_quantity.toLocaleString() }}</td>
              <td>{{ formatDateForDisplay(item.date_finished) }}</td>
              <td>
                <button @click="handleDelete(item.finished_product_id)" class="btn btn-danger btn-sm">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="finishedProducts.length === 0" class="empty-state">
          <p>No finished product data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../utils/dateFormat'

const form = ref({
  product_id: null,
  lot_id: null,
  finished_quantity: null,
  date_finished: getTodayFormatted(),
})

const finishedProducts = ref([])

const loadFinishedProducts = async () => {
  try {
    const response = await api.get('/warehouse/finished-products')
    finishedProducts.value = response.data
  } catch (error) {
    console.error('Failed to load finished products:', error)
    alert('Failed to load finished products')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id || !form.value.lot_id) {
    alert('Please select product code and lot number')
    return
  }

  try {
    // Convert DD/MM/YYYY format to YYYY-MM-DD for API
    const submitData = {
      ...form.value,
      date_finished: formatDateForApi(form.value.date_finished)
    }

    await api.post('/warehouse/finished-products', submitData)
    alert('Finished product registered successfully')
    form.value = {
      product_id: null,
      lot_id: null,
      finished_quantity: null,
      date_finished: getTodayFormatted(),
    }
    await loadFinishedProducts()
  } catch (error) {
    console.error('Failed to create finished product:', error)
    alert('Failed to register finished product')
  }
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this finished product?')) {
    return
  }

  try {
    await api.delete(`/warehouse/finished-products/${id}`)
    alert('Deleted successfully')
    await loadFinishedProducts()
  } catch (error) {
    console.error('Failed to delete finished product:', error)
    alert('Failed to delete')
  }
}

onMounted(() => {
  loadFinishedProducts()
})
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
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

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
