<template>
  <AppLayout>
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
          <button class="btn btn-secondary" @click="downloadCSV">Download CSV</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Employee No</th>
              <th>Name</th>
              <th>Password</th>
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
                <span v-if="employee.has_password" class="status-has-password">●</span>
                <span v-else class="status-no-password">-</span>
              </td>
              <td>
                <span :class="employee.is_active ? 'status-active' : 'status-inactive'">
                  {{ employee.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                  <button class="btn btn-secondary btn-sm" @click="handleEdit(employee)">Edit</button>
                  <button
                    v-if="employee.has_password"
                    class="btn btn-warning btn-sm"
                    @click="handleRevokePassword(employee)"
                  >
                    Revoke
                  </button>
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

      <!-- Password Modal -->
      <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
        <div class="modal-content">
          <h3>Account Created</h3>
          <div class="password-info">
            <div class="info-row">
              <label>Login ID:</label>
              <div class="copyable-field">
                <input type="text" :value="passwordModalData.loginId" readonly />
                <button class="btn btn-secondary btn-sm" @click="copyToClipboard(passwordModalData.loginId)">Copy</button>
              </div>
            </div>
            <div class="info-row">
              <label>Password:</label>
              <div class="copyable-field">
                <input type="text" :value="passwordModalData.password" readonly />
                <button class="btn btn-secondary btn-sm" @click="copyToClipboard(passwordModalData.password)">Copy</button>
              </div>
            </div>
          </div>
          <p class="warning-text">Please save this password immediately. It cannot be retrieved later.</p>
          <button class="btn btn-primary" @click="closePasswordModal">Close</button>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/common/AppLayout.vue'
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

// Password modal state
const showPasswordModal = ref(false)
const passwordModalData = ref({
  loginId: '',
  password: ''
})

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
        passwordModalData.value = {
          loginId: response.data.employee_no,
          password: response.data.generated_password
        }
        showPasswordModal.value = true
      } else {
        alert('Employee updated successfully')
      }
    } else {
      const response = await api.post('/master/employees', form.value)
      if (response.data.generated_password) {
        passwordModalData.value = {
          loginId: response.data.employee_no,
          password: response.data.generated_password
        }
        showPasswordModal.value = true
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

const handleRevokePassword = async (employee) => {
  if (!confirm(`Are you sure you want to revoke password for ${employee.name} (${employee.employee_no})?\n\nThis will disable their login access.`)) {
    return
  }

  try {
    await api.post(`/master/employees/${employee.employee_id}/revoke-password`)
    alert('Password revoked successfully')
    await loadEmployees()
  } catch (error) {
    console.error('Failed to revoke password:', error)
    const detail = error.response?.data?.detail || 'Failed to revoke password'
    alert(detail)
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  } catch (error) {
    console.error('Failed to copy:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('Copied to clipboard!')
  }
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordModalData.value = { loginId: '', password: '' }
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

const downloadCSV = async () => {
  try {
    const response = await api.get('/master/employees', { params: { limit: 100000 } })
    const allData = response.data
    if (allData.length === 0) {
      alert('No data to download')
      return
    }
    const headers = ['Employee ID', 'Employee No', 'Name', 'Status']
    const rows = allData.map(e => [
      e.employee_id,
      `"${(e.employee_no || '').replace(/"/g, '""')}"`,
      `"${(e.name || '').replace(/"/g, '""')}"`,
      e.is_active ? 'Active' : 'Inactive'
    ])
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'employees.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download CSV:', error)
    alert('Failed to download CSV')
  }
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

.status-has-password {
  color: var(--success);
  font-weight: 600;
}

.status-no-password {
  color: var(--text-secondary);
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover {
  background: #e67e22;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: var(--spacing-xl);
  border-radius: 8px;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--success);
}

.password-info {
  background: var(--background-secondary);
  padding: var(--spacing-md);
  border-radius: 4px;
  margin-bottom: var(--spacing-md);
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row label {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.copyable-field {
  display: flex;
  gap: var(--spacing-sm);
}

.copyable-field input {
  flex: 1;
  padding: var(--spacing-sm);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: monospace;
  font-size: var(--font-size-base);
  background: white;
}

.warning-text {
  color: var(--error);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-lg);
}
</style>
