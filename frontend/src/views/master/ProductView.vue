<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Product Code Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Product</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Product Code</label>
              <input v-model="form.product_code" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Customer Name</label>
              <AutocompleteInput
                v-model="form.customer_id"
                endpoint="/master/autocomplete/customers"
                display-field="name"
                value-field="id"
                placeholder="Enter Customer Name..."
                required
                @select="handleCustomerSelect"
              />
            </div>
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
              <input v-model="form.is_active" type="checkbox" />
              <span>Active</span>
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Product List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); flex-wrap: wrap;">
          <input
            v-model="searchProductCode"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Product Code..."
            style="width: 200px;"
          />
          <input
            v-model="searchCustomerName"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Customer..."
            style="width: 200px;"
          />
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Product Code</th>
              <th>Customer Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.product_id">
              <td>{{ formatTimestamp(product.timestamp) }}</td>
              <td>
                <CopyableText :text="product.product_code" />
              </td>
              <td>{{ product.customer_name }}</td>
              <td>
                <span :class="product.is_active ? 'status-active' : 'status-inactive'">
                  {{ product.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <router-link :to="`/master/products/${product.product_id}`" class="btn btn-primary btn-sm">
                  Details
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="products.length === 0" class="empty-state">
          <p>No product data found</p>
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
  product_code: '',
  customer_id: null,
  is_active: true,
})

const products = ref([])
const searchProductCode = ref('')
const searchCustomerName = ref('')
const selectedCustomer = ref(null)

const loadProducts = async () => {
  try {
    const params = {}
    if (searchProductCode.value) {
      params.product_code = searchProductCode.value
    }
    if (searchCustomerName.value) {
      params.customer_name = searchCustomerName.value
    }
    const response = await api.get('/master/products', { params })
    products.value = response.data
  } catch (error) {
    console.error('Failed to load products:', error)
    alert('Failed to load products')
  }
}

const handleCustomerSelect = (customer) => {
  selectedCustomer.value = customer
}

const handleSubmit = async () => {
  if (!form.value.customer_id) {
    alert('Please select a customer')
    return
  }

  try {
    await api.post('/master/products', form.value)
    alert('Product registered successfully')
    form.value = {
      product_code: '',
      customer_id: null,
      is_active: true,
    }
    selectedCustomer.value = null
    await loadProducts()
  } catch (error) {
    console.error('Failed to create product:', error)
    alert('Failed to register product')
  }
}

const handleSearch = () => {
  loadProducts()
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.status-active {
  color: var(--success);
  font-weight: 600;
}

.status-inactive {
  color: var(--text-secondary);
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
</style>
