<template>
  <AppLayout>
      <h1 class="page-title">Mold - Broken Mold Management</h1>

      <!-- Broken Mold Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Broken Mold</h2>
        <form @submit.prevent="handleSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Process ID</label>
            <input v-model.number="form.process_id" class="form-input" type="number" required />
          </div>
          <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Broken Date</label>
            <input v-model="form.date_broken" class="form-input" type="text" placeholder="DD/MM/YYYY" required />
          </div>
          <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Desired Repair</label>
            <input v-model="form.date_hope_repaired" class="form-input" type="text" placeholder="DD/MM/YYYY" />
          </div>
          <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Scheduled Repair</label>
            <input v-model="form.date_schedule_repaired" class="form-input" type="text" placeholder="DD/MM/YYYY" />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Note</label>
            <input v-model="form.note" class="form-input" type="text" />
          </div>
          <div>
            <button type="submit" class="btn btn-primary">Register</button>
          </div>
        </form>
      </div>

      <!-- Broken Mold List -->
      <div class="card">
        <h2>Broken Mold List</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product Code</th>
              <th>Process Name</th>
              <th>Process No</th>
              <th>Broken Date</th>
              <th>Desired Repair</th>
              <th>Scheduled Repair</th>
              <th>Note</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in brokenMolds" :key="item.broken_mold_id">
              <td>{{ item.broken_mold_id }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.process_name || '-' }}</td>
              <td>{{ item.process_no || '-' }}</td>
              <td>{{ formatDateForDisplay(item.date_broken) }}</td>
              <td>{{ item.date_hope_repaired ? formatDateForDisplay(item.date_hope_repaired) : '-' }}</td>
              <td>{{ item.date_schedule_repaired ? formatDateForDisplay(item.date_schedule_repaired) : '-' }}</td>
              <td>{{ item.note || '-' }}</td>
              <td>
                <button @click="handleDelete(item.broken_mold_id)" class="btn btn-danger btn-sm">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="brokenMolds.length === 0" class="empty-state">
          <p>No broken mold data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../utils/dateFormat'

const form = ref({
  process_id: null,
  date_broken: getTodayFormatted(),
  date_hope_repaired: '',
  date_schedule_repaired: '',
  note: '',
})

const brokenMolds = ref([])

const loadBrokenMolds = async () => {
  try {
    const response = await api.get('/mold/broken-molds')
    brokenMolds.value = response.data
  } catch (error) {
    console.error('Failed to load broken molds:', error)
    alert('Failed to load broken mold data')
  }
}

const handleSubmit = async () => {
  try {
    // Convert DD/MM/YYYY format to YYYY-MM-DD for API
    const submitData = {
      ...form.value,
      date_broken: formatDateForApi(form.value.date_broken),
      date_hope_repaired: form.value.date_hope_repaired ? formatDateForApi(form.value.date_hope_repaired) : '',
      date_schedule_repaired: form.value.date_schedule_repaired ? formatDateForApi(form.value.date_schedule_repaired) : ''
    }

    await api.post('/mold/broken-molds', submitData)
    alert('Broken mold registered successfully')
    form.value = {
      process_id: null,
      date_broken: getTodayFormatted(),
      date_hope_repaired: '',
      date_schedule_repaired: '',
      note: '',
    }
    await loadBrokenMolds()
  } catch (error) {
    console.error('Failed to create broken mold:', error)
    alert('Failed to register broken mold')
  }
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this broken mold record?')) {
    return
  }

  try {
    await api.delete(`/mold/broken-molds/${id}`)
    alert('Deleted successfully')
    await loadBrokenMolds()
  } catch (error) {
    console.error('Failed to delete broken mold:', error)
    alert('Failed to delete')
  }
}

onMounted(() => {
  loadBrokenMolds()
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
