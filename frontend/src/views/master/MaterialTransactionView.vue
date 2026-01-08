<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material Inventory Transactions</h1>

    <!-- Transaction Form -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>Record Transaction</h2>
      <form @submit.prevent="handleSubmit">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Type</label>
            <select v-model="form.transaction_type" class="form-input" required>
              <option value="IN">IN (Receive)</option>
              <option value="OUT">OUT (Issue)</option>
            </select>
          </div>
          <div style="width: 200px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">LOT</label>
            <AutocompleteInput
              v-model="form.lot_id"
              endpoint="/material/autocomplete/material-lots"
              display-field="lot_no"
              value-field="id"
              placeholder="Search LOT..."
              required
              @select="onLotSelect"
            />
          </div>
          <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Factory</label>
            <AutocompleteInput
              v-model="form.factory_id"
              endpoint="/master/autocomplete/factories"
              display-field="name"
              value-field="id"
              placeholder="Select Factory..."
              required
            />
          </div>
          <div style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Sheet Qty</label>
            <input v-model.number="form.sheet_qty" class="form-input" type="number" min="0" />
          </div>
          <div style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Coil Qty</label>
            <input v-model.number="form.coil_qty" class="form-input" type="number" min="0" />
          </div>
          <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Weight (kg)</label>
            <input v-model.number="form.weight_kg" class="form-input" type="number" min="0" step="0.001" />
          </div>
          <div style="width: 200px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Note</label>
            <input v-model="form.note" class="form-input" type="text" placeholder="Optional note..." />
          </div>
          <div style="display: flex; gap: 8px;">
            <button type="submit" class="btn btn-primary">Record</button>
            <button type="button" class="btn btn-secondary" @click="resetForm">Clear</button>
          </div>
        </div>
      </form>
    </div>

    <!-- Selected LOT Info -->
    <div v-if="selectedLot" class="card info-card" style="margin-bottom: var(--spacing-lg)">
      <h3>Selected LOT Info</h3>
      <div class="info-grid">
        <div><strong>LOT No:</strong> {{ selectedLot.lot_no }}</div>
        <div><strong>Material Code:</strong> {{ selectedLot.material_code }}</div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="card">
      <h2>Transaction History</h2>
      <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); align-items: center; flex-wrap: wrap;">
        <input
          v-model="searchLot"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search LOT No..."
          style="max-width: 175px;"
        />
        <select v-model="filterFactory" @change="handleSearch" class="form-input" style="max-width: 150px;">
          <option :value="null">All Factories</option>
          <option v-for="f in factories" :key="f.factory_id" :value="f.factory_id">
            {{ f.factory_name }}
          </option>
        </select>
        <select v-model="filterType" @change="handleSearch" class="form-input" style="max-width: 120px;">
          <option :value="null">All Types</option>
          <option value="IN">IN</option>
          <option value="OUT">OUT</option>
        </select>
        <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Date</th>
            <th>Type</th>
            <th>LOT No</th>
            <th>Material</th>
            <th>Factory</th>
            <th>Sheet</th>
            <th>Coil</th>
            <th>Weight (kg)</th>
            <th>Note</th>
            <th>User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.transaction_id">
            <td>{{ tx.transaction_id }}</td>
            <td>{{ formatDate(tx.transaction_date) }}</td>
            <td>
              <span :class="tx.transaction_type === 'IN' ? 'status-in' : 'status-out'">
                {{ tx.transaction_type }}
              </span>
            </td>
            <td>{{ tx.lot_no }}</td>
            <td>{{ tx.material_name || tx.material_code }}</td>
            <td>{{ tx.factory_name }}</td>
            <td>{{ tx.sheet_qty || 0 }}</td>
            <td>{{ tx.coil_qty || 0 }}</td>
            <td>{{ tx.weight_kg || 0 }}</td>
            <td>{{ tx.note || '-' }}</td>
            <td>{{ tx.user }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="transactions.length === 0" class="empty-state">
        <p>No transactions found</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import api from '../../utils/api'

const form = ref({
  transaction_type: 'IN',
  lot_id: null,
  factory_id: null,
  sheet_qty: 0,
  coil_qty: 0,
  weight_kg: 0,
  note: '',
})

const transactions = ref([])
const factories = ref([])
const selectedLot = ref(null)
const searchLot = ref('')
const filterFactory = ref(null)
const filterType = ref(null)

const loadTransactions = async () => {
  try {
    const params = { limit: 100 }
    if (filterFactory.value) params.factory_id = filterFactory.value
    if (filterType.value) params.transaction_type = filterType.value
    const response = await api.get('/material/material-transactions', { params })
    transactions.value = response.data
  } catch (error) {
    console.error('Failed to load transactions:', error)
    alert('Failed to load transactions')
  }
}

const loadFactories = async () => {
  try {
    const response = await api.get('/master/autocomplete/factories')
    factories.value = response.data.map(f => ({ factory_id: f.id, factory_name: f.name }))
  } catch (error) {
    console.error('Failed to load factories:', error)
  }
}

const handleSubmit = async () => {
  try {
    if (!form.value.lot_id || !form.value.factory_id) {
      alert('Please select LOT and Factory')
      return
    }
    if (!form.value.sheet_qty && !form.value.coil_qty && !form.value.weight_kg) {
      alert('Please enter at least one quantity')
      return
    }
    await api.post('/material/material-transactions', form.value)
    alert('Transaction recorded successfully')
    resetForm()
    await loadTransactions()
  } catch (error) {
    console.error('Failed to record transaction:', error)
    const detail = error.response?.data?.detail || 'Failed to record transaction'
    alert(detail)
  }
}

const onLotSelect = (lot) => {
  if (lot) {
    selectedLot.value = lot
  }
}

const resetForm = () => {
  form.value = {
    transaction_type: 'IN',
    lot_id: null,
    factory_id: null,
    sheet_qty: 0,
    coil_qty: 0,
    weight_kg: 0,
    note: '',
  }
  selectedLot.value = null
}

const handleSearch = () => {
  loadTransactions()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ja-JP')
}

const downloadCSV = async () => {
  try {
    const params = { limit: 100000 }
    if (filterFactory.value) params.factory_id = filterFactory.value
    if (filterType.value) params.transaction_type = filterType.value
    const response = await api.get('/material/material-transactions', { params })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['ID', 'Date', 'Type', 'LOT No', 'Material Code', 'Material Name', 'Factory', 'Sheet Qty', 'Coil Qty', 'Weight (kg)', 'Note', 'User']
    const rows = allData.map(tx => [
      tx.transaction_id,
      tx.transaction_date,
      tx.transaction_type,
      `"${(tx.lot_no || '').replace(/"/g, '""')}"`,
      `"${(tx.material_code || '').replace(/"/g, '""')}"`,
      `"${(tx.material_name || '').replace(/"/g, '""')}"`,
      `"${(tx.factory_name || '').replace(/"/g, '""')}"`,
      tx.sheet_qty || 0,
      tx.coil_qty || 0,
      tx.weight_kg || 0,
      `"${(tx.note || '').replace(/"/g, '""')}"`,
      `"${(tx.user || '').replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'material_transactions.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

onMounted(() => {
  loadTransactions()
  loadFactories()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

h3 {
  margin-bottom: var(--spacing-sm);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.info-card {
  background: var(--background-secondary);
}

.info-grid {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.status-in {
  background: var(--success);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.status-out {
  background: var(--error);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}
</style>
