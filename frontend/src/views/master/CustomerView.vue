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
        <h2>{{ editingId ? 'Edit Customer' : 'Register Customer' }}</h2>
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
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">
                {{ editingId ? 'Update' : 'Register' }}
              </button>
              <button v-if="editingId" type="button" class="btn btn-secondary" @click="cancelEdit">
                Cancel
              </button>
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
          placeholder="Search Customer..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <button class="btn btn-secondary" @click="downloadCSV" style="margin-left: var(--spacing-md);">
          Download CSV
        </button>
        <table class="table">
          <thead>
            <tr>
              <th>Customer ID</th>
              <th>Customer Name</th>
              <th>Status</th>
              <th>Actions</th>
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
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleEdit(customer)">Edit</button>
                  <button
                    v-if="editingId === customer.customer_id"
                    class="btn btn-danger btn-sm"
                    @click="handleDelete(customer.customer_id)"
                  >
                    Delete
                  </button>
                </div>
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

const editingId = ref(null)
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
    if (editingId.value) {
      await api.put(`/master/customers/${editingId.value}`, form.value)
      alert('Customer updated successfully')
    } else {
      await api.post('/master/customers', form.value)
      alert('Customer registered successfully')
    }
    resetForm()
    loadCustomers()
  } catch (error) {
    console.error('Failed to save customer:', error)
    const detail = error.response?.data?.detail || 'Failed to save customer'
    alert(detail)
  }
}

const handleEdit = (customer) => {
  editingId.value = customer.customer_id
  form.value = {
    customer_name: customer.customer_name,
    is_active: customer.is_active,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this customer?')) return

  try {
    await api.delete(`/master/customers/${id}`)
    alert('Customer deleted successfully')
    loadCustomers()
  } catch (error) {
    console.error('Failed to delete customer:', error)
    const detail = error.response?.data?.detail || 'Failed to delete customer'
    alert(detail)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  form.value = { customer_name: '', is_active: true }
  editingId.value = null
}

const handleSearch = () => {
  loadCustomers(searchQuery.value)
}

const downloadCSV = () => {
  if (customers.value.length === 0) {
    alert('No data to download')
    return
  }

  const headers = ['Customer ID', 'Customer Name', 'Status']
  const rows = customers.value.map(c => [
    c.customer_id,
    `"${c.customer_name.replace(/"/g, '""')}"`, // Escape quotes
    c.is_active ? 'Active' : 'Inactive'
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'customers.csv')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
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
