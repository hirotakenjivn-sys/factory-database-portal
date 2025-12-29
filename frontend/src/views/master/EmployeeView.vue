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
        <h2>{{ editingId ? 'Edit Employee' : 'Register Employee' }}</h2>
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
              <th>Actions</th>
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
              <td>
                <div style="display: flex; gap: 8px;">
                  <button class="btn btn-secondary btn-sm" @click="handleEdit(employee)">Edit</button>
                  <button
                    v-if="editingId === employee.employee_id"
                    class="btn btn-danger btn-sm"
                    @click="handleDelete(employee.employee_id)"
                  >
                    Delete
                  </button>
                </div>
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
  create_password: false,
})

const editingId = ref(null)
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
    if (editingId.value) {
      const response = await api.put(`/master/employees/${editingId.value}`, form.value)
      if (response.data.generated_password) {
        alert(`Employee updated successfully.\n\nNew Password: ${response.data.generated_password}\n\nPlease save this password immediately.`)
      } else {
        alert('Employee updated successfully')
      }
    } else {
      const response = await api.post('/master/employees', form.value)
      if (response.data.generated_password) {
        alert(`Employee registered successfully.\n\nLogin ID: ${response.data.employee_no}\nPassword: ${response.data.generated_password}\n\nPlease save this password immediately.`)
      } else {
        alert('Employee registered successfully')
      }
    }

    resetForm()
    await loadEmployees()
  } catch (error) {
    console.error('Failed to save employee:', error)
    const detail = error.response?.data?.detail || 'Failed to save employee'
    alert(detail)
  }
}

const handleEdit = (employee) => {
  editingId.value = employee.employee_id
  form.value = {
    employee_no: employee.employee_no,
    name: employee.name,
    is_active: employee.is_active,
    create_password: false,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this employee?')) return

  try {
    await api.delete(`/master/employees/${id}`)
    alert('Employee deleted successfully')
    loadEmployees()
  } catch (error) {
    console.error('Failed to delete employee:', error)
    const detail = error.response?.data?.detail || 'Failed to delete employee'
    alert(detail)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  form.value = {
    employee_no: '',
    name: '',
    is_active: true,
    create_password: false,
  }
  editingId.value = null
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
