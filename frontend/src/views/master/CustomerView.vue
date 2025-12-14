<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Customer Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Customer</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Customer Name</label>
              <input v-model="form.customer_name" class="form-input" type="text" required />
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
        <h2>Customer List</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search Customer..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>Customer ID</th>
              <th>Customer Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in customers" :key="customer.customer_id">
              <td>{{ customer.customer_id }}</td>
              <td>{{ customer.customer_name }}</td>
              <td>
                <span :class="customer.is_active ? 'status-active' : 'status-inactive'">
                  {{ customer.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import api from '../../utils/api'

const form = ref({
  customer_name: '',
  is_active: true,
})

const customers = ref([])
const searchQuery = ref('')

const loadCustomers = async (search = '') => {
  try {
    const response = await api.get('/master/customers', {
      params: { search },
    })
    customers.value = response.data
  } catch (error) {
    console.error('Failed to load customers:', error)
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/customers', form.value)
    alert('Customer registered successfully')
    form.value = { customer_name: '', is_active: true }
    loadCustomers()
  } catch (error) {
    console.error('Failed to create customer:', error)
    alert('Failed to register customer')
  }
}

const handleSearch = () => {
  loadCustomers(searchQuery.value)
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.status-active {
  color: var(--success);
  font-weight: 600;
}

.status-inactive {
  color: var(--text-secondary);
}
</style>
