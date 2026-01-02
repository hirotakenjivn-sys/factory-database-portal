<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Process Name Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Process Name</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Process Name</label>
              <input v-model="form.process_name" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Type</label>
              <div style="display: flex; gap: 16px; align-items: center; height: 34px;">
                <label style="display: flex; align-items: center; gap: 4px;">
                  <input v-model="form.day_or_spm" type="radio" :value="true" />
                  <span>SPM</span>
                </label>
                <label style="display: flex; align-items: center; gap: 4px;">
                  <input v-model="form.day_or_spm" type="radio" :value="false" />
                  <span>Day</span>
                </label>
              </div>
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Process Name List</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="Search Process Name..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Process Name</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in processNames" :key="item.process_name_id">
              <td>{{ item.process_name_id }}</td>
              <td>{{ item.process_name }}</td>
              <td>
                <span :class="item.day_or_spm ? 'type-spm' : 'type-day'">
                  {{ item.day_or_spm ? 'SPM' : 'Day' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="processNames.length === 0" class="empty-state">
          <p>No process name data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const form = ref({
  process_name: '',
  day_or_spm: true,
})

const processNames = ref([])
const searchQuery = ref('')

const loadProcessNames = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/process-names', { params })
    processNames.value = response.data
  } catch (error) {
    console.error('Failed to load process names:', error)
    alert('Failed to load process names')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/process-names', form.value)
    alert('Process name registered successfully')
    form.value = {
      process_name: '',
      day_or_spm: true,
    }
    await loadProcessNames()
  } catch (error) {
    console.error('Failed to create process name:', error)
    alert('Failed to register process name')
  }
}

const handleSearch = () => {
  loadProcessNames(searchQuery.value)
}

onMounted(() => {
  loadProcessNames()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.type-spm {
  color: var(--primary);
  font-weight: 600;
}

.type-day {
  color: var(--warning);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
