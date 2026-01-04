<template>
  <AppLayout>
      <h1 class="page-title">Sales - PO Management</h1>

      <!-- Bulk Import -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Bulk Import (Excel Paste)</h2>
        <ClipboardImport @import-success="handleImportSuccess" />
      </div>

      <!-- PO Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editMode ? 'Edit PO' : 'Register PO' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">PO Number</label>
              <input v-model="form.po_number" class="form-input" type="text" required />
            </div>
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
              <label class="form-label" style="margin-bottom: 0;">Quantity</label>
              <input v-model.number="form.po_quantity" class="form-input" type="number" required />
            </div>
            <div style="width: 143px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Delivery Date</label>
              <input v-model="form.delivery_date" class="form-input" type="date" required />
            </div>
            <div style="width: 143px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">PO Received Date</label>
              <input v-model="form.date_receive_po" class="form-input" type="date" required />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">{{ editMode ? 'Update' : 'Register' }}</button>
              <button v-if="editMode" @click="cancelEdit" type="button" class="btn btn-secondary">Cancel</button>
              <button v-if="editMode" @click="handleDelete" type="button" class="btn btn-danger">Delete</button>
              <button @click="calculateDeliveryDate" type="button" class="btn btn-success">📅 Calculate Delivery</button>
            </div>
          </div>
        </form>

        <!-- Delivery Calculation Result -->
        <div v-if="deliveryCalculation" style="margin-top: var(--spacing-md); padding: var(--spacing-md); background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
          <h3 style="margin-bottom: var(--spacing-sm); color: #2e7d32;">📊 Delivery Calculation Result</h3>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-sm); margin-bottom: var(--spacing-md);">
            <div>
              <strong>Start Date:</strong> {{ formatDateForDisplay(deliveryCalculation.start_date) }}
            </div>
            <div>
              <strong>Calculated Date:</strong> <span style="color: #1976d2; font-weight: 600;">{{ formatDateForDisplay(deliveryCalculation.delivery_date) }}</span>
            </div>
            <div>
              <strong>Total Days:</strong> {{ deliveryCalculation.total_days }} days
            </div>
            <div>
              <strong>PO Quantity:</strong> {{ deliveryCalculation.po_quantity.toLocaleString() }}
            </div>
          </div>

          <!-- Process Details -->
          <h4 style="margin-bottom: var(--spacing-sm);">Process Details</h4>
          <div style="overflow-x: auto;">
            <table class="table" style="background: white;">
              <thead>
                <tr>
                  <th>Process No.</th>
                  <th>Process Name</th>
                  <th>Type</th>
                  <th>Days Required</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>DAY/CT</th>
                  <th>Prod. Limit</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="process in deliveryCalculation.processes" :key="process.process_no">
                  <td>{{ process.process_no }}</td>
                  <td>{{ process.process_name }}</td>
                  <td>
                    <span :style="{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.85rem',
                      fontWeight: '600',
                      background: process.process_type === 'DAY' ? '#e3f2fd' : '#fff3e0',
                      color: process.process_type === 'DAY' ? '#1976d2' : '#f57c00'
                    }">
                      {{ process.process_type }}
                    </span>
                  </td>
                  <td>{{ process.days }} days</td>
                  <td>{{ formatDateForDisplay(process.start_date) }}</td>
                  <td>{{ formatDateForDisplay(process.end_date) }}</td>
                  <td>{{ process.rough_cycletime || '-' }}</td>
                  <td>{{ process.production_limit ? process.production_limit.toLocaleString() : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style="margin-top: var(--spacing-sm);">
            <button @click="applyCalculatedDate" class="btn btn-primary btn-sm">Apply Calculated Date</button>
            <button @click="deliveryCalculation = null" class="btn btn-secondary btn-sm" style="margin-left: var(--spacing-sm);">Close</button>
          </div>
        </div>
      </div>

      <!-- PO List -->
      <div class="card">
        <h2>PO List</h2>

        <!-- Search Fields -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md); flex-wrap: wrap;">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">PO Number</label>
            <input
              v-model="searchFilters.po_number"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="Search PO Number..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">Customer Name</label>
            <input
              v-model="searchFilters.customer_name"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="Search Customer..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">Product Code</label>
            <input
              v-model="searchFilters.product_code"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="Search Product Code..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button
              @click="clearSearch"
              class="btn btn-secondary"
              style="padding: 8px 16px; font-size: 0.9rem;"
            >
              Clear
            </button>
          </div>
        </div>

        <table class="table">
          <thead>
            <tr>
              <th>PO Number</th>
              <th>Customer Name</th>
              <th>Product Code</th>
              <th>Quantity</th>
              <th>Delivery Date</th>
              <th>PO Received Date</th>
              <th>Registered Date</th>
              <th>Registered By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="po in poList" :key="po.po_id">
              <td>{{ po.po_number }}</td>
              <td>{{ po.customer_name || '-' }}</td>
              <td>
                <CopyableText v-if="po.product_code" :text="po.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ po.po_quantity.toLocaleString() }}</td>
              <td>{{ formatDateForDisplay(po.delivery_date) }}</td>
              <td>{{ formatDateForDisplay(po.date_receive_po) }}</td>
              <td>{{ formatTimestamp(po.timestamp) }}</td>
              <td>{{ po.user || '-' }}</td>
              <td>
                <button @click="editPO(po)" class="btn btn-sm btn-secondary">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="poList.length === 0" class="empty-state">
          <p>No PO data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import ClipboardImport from '../components/sales/ClipboardImport.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../utils/dateFormat'

const editMode = ref(false)
const editingPoId = ref(null)

const form = ref({
  po_number: '',
  product_id: null,
  po_quantity: null,
  delivery_date: '',
  date_receive_po: new Date().toISOString().split('T')[0], // YYYY-MM-DD format for type="date"
})

const poList = ref([])
const searchFilters = ref({
  po_number: '',
  customer_name: '',
  product_code: ''
})

// Delivery calculation
const deliveryCalculation = ref(null)

let searchTimeout = null

const loadPOs = async () => {
  try {
    const params = {}

    if (searchFilters.value.po_number) {
      params.po_number = searchFilters.value.po_number
    }
    if (searchFilters.value.customer_name) {
      params.customer_name = searchFilters.value.customer_name
    }
    if (searchFilters.value.product_code) {
      params.product_code = searchFilters.value.product_code
    }

    const response = await api.get('/sales/po', { params })
    poList.value = response.data
  } catch (error) {
    console.error('Failed to load POs:', error)
  }
}

const handleSearch = () => {
  // Debounce (search after 300ms delay)
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadPOs()
  }, 300)
}

const clearSearch = () => {
  searchFilters.value = {
    po_number: '',
    customer_name: '',
    product_code: ''
  }
  loadPOs()
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('Please select a Product Code')
    return
  }

  try {
    if (editMode.value) {
      // Update
      await api.put(`/sales/po/${editingPoId.value}`, form.value)
      alert('PO updated successfully')
      cancelEdit()
    } else {
      // Register
      await api.post('/sales/po', form.value)
      alert('PO registered successfully')
      form.value = {
        po_number: '',
        product_id: null,
        po_quantity: null,
        delivery_date: '',
        date_receive_po: new Date().toISOString().split('T')[0],
      }
    }
    loadPOs()
  } catch (error) {
    console.error('Failed to save PO:', error)
    alert(editMode.value ? 'Failed to update PO' : 'Failed to register PO')
  }
}

const editPO = (po) => {
  editMode.value = true
  editingPoId.value = po.po_id
  form.value = {
    po_number: po.po_number,
    product_id: po.product_id,
    po_quantity: po.po_quantity,
    delivery_date: po.delivery_date,
    date_receive_po: po.date_receive_po,
  }
  // Scroll to top to show form
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  editMode.value = false
  editingPoId.value = null
  form.value = {
    po_number: '',
    product_id: null,
    po_quantity: null,
    delivery_date: '',
    date_receive_po: new Date().toISOString().split('T')[0],
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this PO?')) {
    return
  }

  try {
    await api.delete(`/sales/po/${editingPoId.value}`)
    alert('PO deleted successfully')
    cancelEdit()
    loadPOs()
  } catch (error) {
    console.error('Failed to delete PO:', error)
    alert('Failed to delete PO')
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}`
}

const calculateDeliveryDate = async () => {
  // Validation
  if (!form.value.product_id) {
    alert('Please select a Product Code')
    return
  }
  if (!form.value.po_quantity || form.value.po_quantity <= 0) {
    alert('Please enter Quantity')
    return
  }
  if (!form.value.date_receive_po) {
    alert('Please enter PO Received Date')
    return
  }

  try {
    const response = await api.post('/sales/po/calculate-delivery', {
      product_id: form.value.product_id,
      po_quantity: form.value.po_quantity,
      start_date: form.value.date_receive_po
    })
    deliveryCalculation.value = response.data
    console.log('Delivery calculation result:', response.data)
  } catch (error) {
    console.error('Failed to calculate delivery date:', error)
    alert('Failed to calculate delivery date: ' + (error.response?.data?.detail || error.message))
  }
}

const applyCalculatedDate = () => {
  if (deliveryCalculation.value && deliveryCalculation.value.delivery_date) {
    form.value.delivery_date = deliveryCalculation.value.delivery_date
    alert('Calculated delivery date applied')
  }
}

const handleImportSuccess = () => {
  loadPOs()
}

onMounted(() => {
  loadPOs()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.85rem;
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}
</style>
