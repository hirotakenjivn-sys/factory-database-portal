<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Supplier Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editMode ? 'Edit Supplier' : 'Register Supplier' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Supplier Name</label>
              <input v-model="form.supplier_name" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Business Type</label>
              <input v-model="form.supplier_business" class="form-input" type="text" />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">{{ editMode ? 'Update' : 'Register' }}</button>
              <button v-if="editMode" @click="cancelEdit" type="button" class="btn btn-secondary">Cancel</button>
              <button v-if="editMode" @click="handleDelete" type="button" class="btn btn-danger">Delete</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Supplier List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center;">
          <input
            v-model="searchQuery"
            class="form-input"
            type="text"
            placeholder="Search Supplier..."
            style="max-width: 175px;"
          />
          <input
            v-model="searchBusiness"
            class="form-input"
            type="text"
            placeholder="Search Business Type..."
            style="max-width: 175px;"
          />
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Supplier ID</th>
              <th>Supplier Name</th>
              <th>Business Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="supplier in suppliers" :key="supplier.supplier_id">
              <td>{{ supplier.supplier_id }}</td>
              <td>{{ supplier.supplier_name }}</td>
              <td>{{ supplier.supplier_business || '-' }}</td>
              <td>
                <button @click="editSupplier(supplier)" class="btn btn-sm btn-secondary" style="margin-right: 4px;">Edit</button>
                <button @click="deleteSupplier(supplier)" class="btn btn-sm btn-danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="suppliers.length === 0" class="empty-state">
          <p>No supplier data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const form = ref({
  supplier_name: '',
  supplier_business: '',
})

const editMode = ref(false)
const editingSupplierId = ref(null)

const allSuppliers = ref([])
const searchQuery = ref('')
const searchBusiness = ref('')

// フィルタリング
const suppliers = computed(() => {
  return allSuppliers.value.filter(supplier => {
    const nameMatch = !searchQuery.value ||
      supplier.supplier_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const businessMatch = !searchBusiness.value ||
      (supplier.supplier_business || '').toLowerCase().includes(searchBusiness.value.toLowerCase())
    return nameMatch && businessMatch
  })
})

const loadSuppliers = async () => {
  try {
    const response = await api.get('/master/suppliers')
    allSuppliers.value = response.data
  } catch (error) {
    console.error('Failed to load suppliers:', error)
    alert('Failed to load suppliers')
  }
}

const handleSubmit = async () => {
  try {
    if (editMode.value) {
      await api.put(`/master/suppliers/${editingSupplierId.value}`, form.value)
      alert('Supplier updated successfully')
      cancelEdit()
    } else {
      await api.post('/master/suppliers', form.value)
      alert('Supplier registered successfully')
      form.value = {
        supplier_name: '',
        supplier_business: '',
      }
    }
    await loadSuppliers()
  } catch (error) {
    console.error('Failed to save supplier:', error)
    alert(editMode.value ? 'Failed to update supplier' : 'Failed to register supplier')
  }
}

const editSupplier = (supplier) => {
  editMode.value = true
  editingSupplierId.value = supplier.supplier_id
  form.value = {
    supplier_name: supplier.supplier_name,
    supplier_business: supplier.supplier_business || '',
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  editMode.value = false
  editingSupplierId.value = null
  form.value = {
    supplier_name: '',
    supplier_business: '',
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this supplier?')) {
    return
  }
  try {
    await api.delete(`/master/suppliers/${editingSupplierId.value}`)
    alert('Supplier deleted successfully')
    cancelEdit()
    await loadSuppliers()
  } catch (error) {
    console.error('Failed to delete supplier:', error)
    alert('Failed to delete supplier')
  }
}

const deleteSupplier = async (supplier) => {
  if (!confirm(`Are you sure you want to delete "${supplier.supplier_name}"?`)) {
    return
  }
  try {
    await api.delete(`/master/suppliers/${supplier.supplier_id}`)
    alert('Supplier deleted successfully')
    await loadSuppliers()
  } catch (error) {
    console.error('Failed to delete supplier:', error)
    alert('Failed to delete supplier')
  }
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/master/suppliers', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['Supplier ID', 'Supplier Name', 'Business Type']
    const rows = allData.map(s => [
      s.supplier_id,
      `"${(s.supplier_name || '').replace(/"/g, '""')}"`,
      `"${(s.supplier_business || '').replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'suppliers.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadSuppliers()
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

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
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
