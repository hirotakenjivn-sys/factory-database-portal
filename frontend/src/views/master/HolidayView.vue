<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Holiday Master</h1>

      <!-- Tab Navigation -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'holidays'"
          :class="{ active: activeTab === 'holidays' }"
          class="tab-btn"
        >
          Register Holiday
        </button>
        <button
          @click="activeTab = 'holiday-types'"
          :class="{ active: activeTab === 'holiday-types' }"
          class="tab-btn"
        >
          Holiday Type Management
        </button>
      </div>

      <!-- Holiday Registration Tab -->
      <div v-if="activeTab === 'holidays'">
        <!-- Holiday Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Holiday</h2>
        <form @submit.prevent="handleSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Holiday Date</label>
            <input v-model="form.date_holiday" class="form-input" type="text" placeholder="DD/MM/YYYY" required />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Holiday Type</label>
            <select v-model.number="form.holiday_type_id" class="form-input" required>
              <option value="">Select Type</option>
              <option v-for="type in holidayTypes" :key="type.holiday_type_id" :value="type.holiday_type_id">
                {{ type.date_type }}
              </option>
            </select>
          </div>
          <div>
            <button type="submit" class="btn btn-primary">Register</button>
          </div>
        </form>
      </div>

      <!-- Holiday List -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md);">
          <h2 style="margin-bottom: 0;">Holiday List</h2>
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th @click="toggleSort" class="sortable">
                Holiday Date {{ sortOrder === 'asc' ? '▲' : '▼' }}
              </th>
              <th>Holiday Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sortedHolidays" :key="item.calendar_id">
              <td>{{ item.calendar_id }}</td>
              <td>{{ formatDateForDisplay(item.date_holiday) }}</td>
              <td>{{ item.date_type }}</td>
              <td>
                <button @click="handleDelete(item.calendar_id)" class="btn btn-danger btn-sm">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="holidays.length === 0" class="empty-state">
          <p>No holiday data found</p>
        </div>
      </div>
      </div>

      <!-- Holiday Type Management Tab -->
      <div v-if="activeTab === 'holiday-types'">
        <!-- Holiday Type Registration Form -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>Register Holiday Type</h2>
          <form @submit.prevent="handleHolidayTypeSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Holiday Type Name</label>
              <input v-model="holidayTypeForm.date_type" class="form-input" type="text" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </form>
        </div>

        <!-- Holiday Type List -->
        <div class="card">
          <h2>Holiday Type List</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Holiday Type Name</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="type in holidayTypes" :key="type.holiday_type_id">
                <td>{{ type.holiday_type_id }}</td>
                <td>{{ type.date_type }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="holidayTypes.length === 0" class="empty-state">
            <p>No holiday type data found</p>
          </div>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../../utils/dateFormat'

const activeTab = ref('holidays')

const form = ref({
  date_holiday: getTodayFormatted(),
  holiday_type_id: '',
})

const holidayTypeForm = ref({
  date_type: '',
})

const holidayTypes = ref([])
const holidays = ref([])
const sortOrder = ref('asc')

const sortedHolidays = computed(() => {
  return [...holidays.value].sort((a, b) => {
    const dateA = new Date(a.date_holiday)
    const dateB = new Date(b.date_holiday)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

const toggleSort = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const downloadCSV = async () => {
  try {
    const response = await api.get('/schedule/calendar', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    // Sort by date
    const sorted = [...allData].sort((a, b) => {
      const dateA = new Date(a.date_holiday)
      const dateB = new Date(b.date_holiday)
      return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
    })
    const headers = ['ID', 'Holiday Date', 'Holiday Type']
    const rows = sorted.map(h => [
      h.calendar_id,
      `"${formatDateForDisplay(h.date_holiday)}"`,
      `"${(h.date_type || '').replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'holidays.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
}

const loadHolidayTypes = async () => {
  try {
    const response = await api.get('/schedule/holiday-types')
    holidayTypes.value = response.data
  } catch (error) {
    console.error('Failed to load holiday types:', error)
  }
}

const loadHolidays = async () => {
  try {
    const response = await api.get('/schedule/calendar')
    holidays.value = response.data
  } catch (error) {
    console.error('Failed to load holidays:', error)
    alert('Failed to load holidays')
  }
}

const handleSubmit = async () => {
  try {
    // Convert DD/MM/YYYY format to YYYY-MM-DD format for API submission
    const submitData = {
      ...form.value,
      date_holiday: formatDateForApi(form.value.date_holiday)
    }

    await api.post('/schedule/calendar', submitData)
    alert('Holiday registered successfully')
    form.value = {
      date_holiday: getTodayFormatted(),
      holiday_type_id: '',
    }
    await loadHolidays()
  } catch (error) {
    console.error('Failed to create holiday:', error)
    alert('Failed to register holiday')
  }
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this holiday?')) {
    return
  }

  try {
    await api.delete(`/schedule/calendar/${id}`)
    alert('Holiday deleted successfully')
    await loadHolidays()
  } catch (error) {
    console.error('Failed to delete holiday:', error)
    alert('Failed to delete holiday')
  }
}

const handleHolidayTypeSubmit = async () => {
  try {
    await api.post('/schedule/holiday-types', holidayTypeForm.value)
    alert('Holiday type registered successfully')
    holidayTypeForm.value = {
      date_type: '',
    }
    await loadHolidayTypes()
  } catch (error) {
    console.error('Failed to create holiday type:', error)
    alert('Failed to register holiday type')
  }
}

onMounted(() => {
  loadHolidayTypes()
  loadHolidays()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
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

.tabs {
  display: flex;
  gap: var(--spacing-sm);
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  padding: var(--spacing-md) var(--spacing-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--background-hover);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background: var(--background-hover);
}
</style>
