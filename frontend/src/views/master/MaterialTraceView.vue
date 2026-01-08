<template>
  <AppLayout>
    <div style="margin-bottom: var(--spacing-lg)">
      <router-link to="/master" class="btn btn-secondary">&larr; Back to Master Menu</router-link>
    </div>

    <h1 class="page-title">Material Trace / History</h1>

    <!-- Search Form -->
    <div class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>Search LOT</h2>
      <div style="display: flex; gap: var(--spacing-sm); align-items: flex-end; flex-wrap: wrap;">
        <div style="width: 250px; display: flex; flex-direction: column; gap: 2px;">
          <label class="form-label" style="margin-bottom: 0;">LOT</label>
          <AutocompleteInput
            v-model="selectedLotId"
            endpoint="/material/autocomplete/material-lots"
            display-field="lot_no"
            value-field="id"
            placeholder="Search LOT No..."
            @select="onLotSelect"
          />
        </div>
        <button class="btn btn-primary" @click="searchLot" :disabled="!selectedLotId">Search</button>
        <button class="btn btn-secondary" @click="clearSearch">Clear</button>
      </div>
    </div>

    <!-- LOT Info -->
    <div v-if="lotInfo" class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>LOT Information</h2>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">LOT No:</span>
          <span class="info-value">{{ lotInfo.lot_no }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Material Code:</span>
          <span class="info-value">{{ lotInfo.material_code }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Material:</span>
          <span class="info-value">{{ lotInfo.material_name || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Supplier:</span>
          <span class="info-value">{{ lotInfo.supplier_name || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Received Date:</span>
          <span class="info-value">{{ lotInfo.received_date || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Inspection:</span>
          <span :class="'status-' + (lotInfo.inspection_status || 'pending').toLowerCase()">
            {{ lotInfo.inspection_status || 'PENDING' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Current Stock for LOT -->
    <div v-if="lotStock.length > 0" class="card" style="margin-bottom: var(--spacing-lg)">
      <h2>Current Stock by Factory</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Factory</th>
            <th>Sheet Qty</th>
            <th>Coil Qty</th>
            <th>Weight (kg)</th>
            <th>Last Updated</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in lotStock" :key="s.factory_id">
            <td>{{ s.factory_name }}</td>
            <td :class="{ 'negative': s.sheet_qty < 0 }">{{ s.sheet_qty || 0 }}</td>
            <td :class="{ 'negative': s.coil_qty < 0 }">{{ s.coil_qty || 0 }}</td>
            <td :class="{ 'negative': s.weight_kg < 0 }">{{ s.weight_kg || 0 }}</td>
            <td>{{ formatDate(s.last_updated) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Transaction History -->
    <div v-if="transactions.length > 0" class="card">
      <h2>Transaction History</h2>
      <div class="timeline">
        <div v-for="tx in transactions" :key="tx.transaction_id" class="timeline-item">
          <div class="timeline-marker" :class="tx.transaction_type === 'IN' ? 'marker-in' : 'marker-out'"></div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span :class="tx.transaction_type === 'IN' ? 'type-in' : 'type-out'">
                {{ tx.transaction_type }}
              </span>
              <span class="timeline-date">{{ formatDate(tx.transaction_date) }}</span>
            </div>
            <div class="timeline-body">
              <div><strong>Factory:</strong> {{ tx.factory_name }}</div>
              <div class="qty-row">
                <span v-if="tx.sheet_qty">Sheet: {{ tx.sheet_qty }}</span>
                <span v-if="tx.coil_qty">Coil: {{ tx.coil_qty }}</span>
                <span v-if="tx.weight_kg">Weight: {{ tx.weight_kg }} kg</span>
              </div>
              <div v-if="tx.note" class="note">Note: {{ tx.note }}</div>
              <div class="user">By: {{ tx.user }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedLotId && transactions.length === 0 && lotInfo" class="card">
      <div class="empty-state">
        <p>No transaction history found for this LOT</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import api from '../../utils/api'

const selectedLotId = ref(null)
const lotInfo = ref(null)
const lotStock = ref([])
const transactions = ref([])

const onLotSelect = (lot) => {
  if (lot) {
    selectedLotId.value = lot.id
  }
}

const searchLot = async () => {
  if (!selectedLotId.value) return

  try {
    // Load lot info
    const lotsResponse = await api.get('/material/material-lots', { params: { limit: 1000 } })
    const lot = lotsResponse.data.find(l => l.lot_id === selectedLotId.value)
    lotInfo.value = lot || null

    // Load stock for this lot
    const stockResponse = await api.get(`/material/material-stock/by-lot/${selectedLotId.value}`)
    lotStock.value = stockResponse.data

    // Load transaction history
    const txResponse = await api.get(`/material/material-transactions/by-lot/${selectedLotId.value}`)
    transactions.value = txResponse.data
  } catch (error) {
    console.error('Failed to load lot data:', error)
    alert('Failed to load lot data')
  }
}

const clearSearch = () => {
  selectedLotId.value = null
  lotInfo.value = null
  lotStock.value = []
  transactions.value = []
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ja-JP')
}
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.info-item {
  display: flex;
  gap: var(--spacing-sm);
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.info-value {
  font-weight: bold;
}

.negative {
  color: var(--error);
  font-weight: bold;
}

.status-pending {
  background: #f39c12;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.status-passed {
  background: var(--success);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.status-failed {
  background: var(--error);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

/* Timeline Styles */
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border);
}

.timeline-item {
  position: relative;
  margin-bottom: var(--spacing-lg);
}

.timeline-marker {
  position: absolute;
  left: -24px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.marker-in {
  background: var(--success);
}

.marker-out {
  background: var(--error);
}

.timeline-content {
  background: var(--background-secondary);
  padding: var(--spacing-md);
  border-radius: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.type-in {
  background: var(--success);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.type-out {
  background: var(--error);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.timeline-date {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.timeline-body {
  font-size: var(--font-size-sm);
}

.qty-row {
  display: flex;
  gap: var(--spacing-md);
  margin: var(--spacing-xs) 0;
}

.note {
  color: var(--text-secondary);
  font-style: italic;
  margin-top: var(--spacing-xs);
}

.user {
  color: var(--text-secondary);
  font-size: 0.9em;
  margin-top: var(--spacing-xs);
}
</style>
