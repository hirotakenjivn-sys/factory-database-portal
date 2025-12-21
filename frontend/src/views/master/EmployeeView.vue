<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← Back to Master Menu</router-link>
      </div>

      <h1 class="page-title">Employee Master</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>Register Employee</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Employee No</label>
              <input v-model="form.employee_no" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Name</label>
              <input v-model="form.name" class="form-input" type="text" required />
            </div>
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
              <input v-model="form.is_active" type="checkbox" id="is_active" />
              <label for="is_active" style="margin: 0; cursor: pointer;">Active</label>
            </div>
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
              <input v-model="form.create_password" type="checkbox" id="create_password" />
              <label for="create_password" style="margin: 0; cursor: pointer;">Create Password</label>
            </div>
            <div>
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>Employee List</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); flex-wrap: wrap;">
          <input
            v-model="searchEmployeeNo"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Employee No..."
            style="width: 200px;"
          />
          <input
            v-model="searchName"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="Search Name..."
            style="width: 200px;"
          />
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Employee No</th>
              <th>Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employees" :key="employee.employee_id">
              <td>{{ employee.employee_id }}</td>
              <td>{{ employee.employee_no }}</td>
              <td>{{ employee.name }}</td>
              <td>
                <span :class="employee.is_active ? 'status-active' : 'status-inactive'">
                  {{ employee.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="employees.length === 0" class="empty-state">
          <p>No employee data found</p>
        </div>
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
  employee_no: '',
  name: '',
  is_active: true,
  create_password: true,
})

const employees = ref([])
const searchEmployeeNo = ref('')
const searchName = ref('')

const loadEmployees = async () => {
  try {
    const params = {}
    if (searchEmployeeNo.value) {
      params.employee_no = searchEmployeeNo.value
    }
    if (searchName.value) {
      params.name = searchName.value
    }
    const response = await api.get('/master/employees', { params })
    employees.value = response.data
  } catch (error) {
    console.error('Failed to load employees:', error)
    alert('Failed to load employees')
  }
}

const handleSubmit = async () => {
  try {
    const response = await api.post('/master/employees', form.value)
    
    if (response.data.generated_password) {
      alert(`Employee registered successfully.\n\nLogin ID: ${response.data.employee_no}\nPassword: ${response.data.generated_password}\n\nPlease save this password immediately.`)
    } else {
      alert('Employee registered successfully')
    }

    form.value = {
      employee_no: '',
      name: '',
      is_active: true,
      create_password: true,
    }
    await loadEmployees()
  } catch (error) {
    console.error('Failed to create employee:', error)
    alert('Failed to register employee')
  }
}

const handleSearch = () => {
  loadEmployees()
}

onMounted(() => {
  loadEmployees()
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
</style>
