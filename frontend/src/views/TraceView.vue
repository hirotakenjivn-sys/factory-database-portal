<template>
  <AppLayout>
      <div class="trace-view">
        <div class="trace-header">
          <h1>Press Record Registration</h1>
          <p class="trace-subtitle">Register trace information for in-house operations</p>
        </div>

        <!-- Registration Form -->
        <div class="form-section">
          <!-- Employee Error Warning -->
          <div v-if="employeeError" class="alert alert-warning" style="margin-bottom: 1.5rem;">
            <strong>⚠ Warning:</strong> {{ employeeError }}
            <br>
            <small>Please verify that the current login user is registered in the Employee Master.</small>
          </div>

          <form @submit.prevent="submitTrace" class="trace-form">
            <div class="form-row">
              <div class="form-group">
                <label for="product-code">Product Code <span class="required">*</span></label>
                <AutocompleteInput
                  v-model="form.product_code"
                  endpoint="/master/autocomplete/products"
                  display-field="product_code"
                  value-field="product_code"
                  placeholder="e.g. P-12345"
                  required
                  @select="onProductSelect"
                />
              </div>

              <div class="form-group">
                <label for="customer-name">Customer Name</label>
                <input
                  id="customer-name"
                  v-model="customerName"
                  type="text"
                  class="form-control"
                  readonly
                  placeholder="Auto-displayed after entering product code"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="lot-number">Lot Number <span class="required">*</span></label>
                <input
                  id="lot-number"
                  v-model="form.lot_number"
                  type="text"
                  class="form-control"
                  placeholder="e.g. SECC 120923 JFE"
                  required
                >
              </div>

              <div class="form-group">
                <label for="process">Process <span class="required">*</span></label>
                <select id="process" v-model="form.process_id" class="form-control" required>
                  <option value="">Please select</option>
                  <option v-for="process in filteredProcesses" :key="process.process_id" :value="process.process_id">
                    {{ process.process_name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="employee">Operator <span class="required">*</span></label>
                <input
                  id="employee"
                  v-model="employeeName"
                  type="text"
                  class="form-control"
                  readonly
                  :class="{ 'error-field': !form.employee_id || employeeError }"
                >
                <span v-if="employeeError" class="error-text">
                  {{ employeeError }}
                </span>
              </div>

              <div class="form-group">
                <label for="date">Work Date <span class="required">*</span></label>
                <input
                  id="date"
                  v-model="form.date"
                  type="date"
                  class="form-control"
                  required
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="ok-quantity">OK Quantity <span class="required">*</span></label>
                <input
                  id="ok-quantity"
                  v-model.number="form.ok_quantity"
                  type="number"
                  min="0"
                  class="form-control"
                  placeholder="Enter quantity"
                  required
                >
              </div>

              <div class="form-group">
                <label for="ng-quantity">NG Quantity <span class="required">*</span></label>
                <input
                  id="ng-quantity"
                  v-model.number="form.ng_quantity"
                  type="number"
                  min="0"
                  class="form-control"
                  placeholder="Enter quantity"
                  required
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="result">Result <span class="required">*</span></label>
                <select id="result" v-model="form.result" class="form-control" required>
                  <option value="pass">Pass</option>
                  <option value="fail">Fail</option>
                  <option value="rework">Rework</option>
                </select>
              </div>

              <div class="form-group">
                <!-- Empty -->
              </div>
            </div>

            <div class="form-group full-width">
              <label for="note">Note</label>
              <textarea
                id="note"
                v-model="form.note"
                class="form-control"
                rows="3"
                placeholder="Enter notes"
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="button" @click="resetForm" class="btn btn-secondary">
                Clear
              </button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitDisabled">
                {{ submitting ? 'Registering...' : 'Register' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Success/Error Messages -->
        <div v-if="successMessage" class="alert alert-success">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="alert alert-error">
          {{ errorMessage }}
        </div>

        <!-- Registered Trace History -->
        <div v-if="recentTraces.length > 0" class="recent-traces">
          <h2>Recent Registration History</h2>
          <div class="table-container">
            <table class="trace-table">
              <thead>
                <tr>
                  <th>Registered Date</th>
                  <th>Product Code</th>
                  <th>Lot Number</th>
                  <th>Process Name</th>
                  <th>Operator</th>
                  <th>OK Qty</th>
                  <th>NG Qty</th>
                  <th>Result</th>
                  <th>Packing Done</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trace in recentTraces" :key="trace.stamp_trace_id">
                  <td>{{ formatDateTime(trace.timestamp) }}</td>
                  <td>{{ trace.product_code || '-' }}</td>
                  <td>{{ trace.lot_number || '-' }}</td>
                  <td>{{ trace.process_name || '-' }}</td>
                  <td>{{ trace.employee_name || '-' }}</td>
                  <td class="number">{{ trace.ok_quantity }}</td>
                  <td class="number">{{ trace.ng_quantity }}</td>
                  <td>
                    <span class="badge" :class="getResultClass(trace.result)">
                      {{ getResultLabel(trace.result) }}
                    </span>
                  </td>
                  <td style="text-align: center;">
                    <span v-if="trace.done" style="color: green; font-weight: bold;">✔</span>
                    <span v-else style="color: #ccc;">-</span>
                  </td>
                  <td>{{ trace.note || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'

const authStore = useAuthStore()

// マスタデータ
const processList = ref([])
const recentTraces = ref([])

// 表示用
const customerName = ref('')
const employeeName = ref('')
const employeeError = ref('')

// フォーム
const form = ref({
  product_code: '',
  product_id: null,
  lot_number: '',
  process_id: '',
  employee_id: null,
  ok_quantity: null,
  ng_quantity: 0,
  result: 'pass',
  date: new Date().toISOString().split('T')[0],
  note: ''
})

// 状態管理
const submitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// フィルタリングされたリスト
const filteredProcesses = computed(() => {
  if (!form.value.product_id) return []
  const processes = processList.value.filter(process => process.product_id === form.value.product_id)
  // process_no順にソート（工程1から順番に表示）
  return processes.sort((a, b) => a.process_no - b.process_no)
})

// 送信ボタンの無効化条件
const isSubmitDisabled = computed(() => {
  return submitting.value ||
         !form.value.product_id ||
         !form.value.lot_number ||
         !form.value.process_id ||
         !form.value.employee_id ||
         form.value.ok_quantity === null ||
         form.value.ng_quantity === null
})

// イベントハンドラ
const onProductSelect = (product) => {
  if (product) {
    form.value.product_id = product.id
    customerName.value = product.customer_name || ''
    // 製品変更時は工程、ロット番号、数量などをクリア
    form.value.process_id = ''
    form.value.lot_number = ''
    form.value.ok_quantity = null
    form.value.ng_quantity = 0
    form.value.note = ''
  } else {
    // 選択解除時（または入力変更による無効化時）
    // form.value.product_code = '' // AutocompleteInputのv-modelで管理されるため、ここではクリアしない
    customerName.value = ''
    form.value.product_id = null
    form.value.process_id = ''
    form.value.lot_number = ''
    form.value.ok_quantity = null
    form.value.ng_quantity = 0
    form.value.note = ''
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('ja-JP')
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-'
  const date = new Date(dateTimeString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
}

const getResultLabel = (result) => {
  switch (result) {
    case 'pass':
      return 'Pass'
    case 'fail':
      return 'Fail'
    case 'rework':
      return 'Rework'
    default:
      return '-'
  }
}

const getResultClass = (result) => {
  switch (result) {
    case 'pass':
      return 'badge-success'
    case 'fail':
      return 'badge-danger'
    case 'rework':
      return 'badge-warning'
    default:
      return ''
  }
}

const resetForm = () => {
  // 登録後も保持する項目
  const currentEmployeeId = form.value.employee_id
  const currentProductCode = form.value.product_code
  const currentProductId = form.value.product_id
  const currentLotNumber = form.value.lot_number
  const currentProcessId = form.value.process_id

  form.value = {
    product_code: currentProductCode, // プロダクトコードを保持
    product_id: currentProductId, // プロダクトIDを保持
    lot_number: currentLotNumber, // ロット番号を保持
    process_id: currentProcessId, // 工程を保持
    employee_id: currentEmployeeId, // 従業員IDは保持
    ok_quantity: null,
    ng_quantity: 0,
    result: 'pass',
    date: new Date().toISOString().split('T')[0],
    note: ''
  }
  // customerNameは保持（プロダクトコードが保持されているため）
  successMessage.value = ''
  errorMessage.value = ''
}

const submitTrace = async () => {
  // Validation
  if (!form.value.product_id) {
    errorMessage.value = 'Please enter product code'
    return
  }

  if (!form.value.lot_number || form.value.lot_number.trim() === '') {
    errorMessage.value = 'Please enter lot number'
    return
  }

  if (!form.value.process_id) {
    errorMessage.value = 'Please select a process'
    return
  }

  if (!form.value.employee_id) {
    errorMessage.value = 'Operator information not found. Please verify registration in Employee Master.'
    return
  }

  if (form.value.ok_quantity === null || form.value.ok_quantity === '') {
    errorMessage.value = 'Please enter OK quantity'
    return
  }

  if (form.value.ng_quantity === null || form.value.ng_quantity === '') {
    errorMessage.value = 'Please enter NG quantity'
    return
  }

  submitting.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    // Debug: Log data being sent
    const payload = {
      product_id: form.value.product_id,
      lot_number: form.value.lot_number,
      process_id: form.value.process_id,
      employee_id: form.value.employee_id,
      ok_quantity: form.value.ok_quantity,
      ng_quantity: form.value.ng_quantity,
      result: form.value.result,
      date: form.value.date,
      note: form.value.note
    }
    console.log('Trace registration request:', payload)

    // Register trace (production_condition handled by backend)
    await api.post('/trace/stamp-trace-simple', payload)

    successMessage.value = 'Press record registered successfully'
    resetForm()
    await fetchRecentTraces()
  } catch (error) {
    console.error('Trace registration error:', error)
    console.error('Error response:', error.response)
    const errorDetail = error.response?.data?.detail || error.message || 'Failed to register trace'
    errorMessage.value = `Error: ${errorDetail}`
    if (error.response?.status) {
      errorMessage.value += ` (Status: ${error.response.status})`
    }
  } finally {
    submitting.value = false
  }
}

const fetchMasterData = async () => {
  try {
    // Get process list
    const processResponse = await api.get('/process/list')
    processList.value = processResponse.data

    // Set login user information
    if (!authStore.user) {
      employeeError.value = 'Cannot retrieve login information. Please login again.'
      return
    }

    employeeName.value = authStore.user.username

    // Get employee ID from username (employee number)
    try {
      // Search by employee number instead of fetching all (pagination workaround)
      const employeeResponse = await api.get('/master/employees', {
        params: { employee_no: authStore.user.username }
      })

      // Find exact match since search is partial match
      const employee = employeeResponse.data.find(emp =>
        emp.employee_no === authStore.user.username
      )

      if (employee) {
        form.value.employee_id = employee.employee_id
        employeeError.value = ''
      } else {
        employeeError.value = 'Employee information not found for login ID.'
        errorMessage.value = 'Could not retrieve operator information.'
      }
    } catch (error) {
      console.error('Employee information fetch error:', error)
      employeeError.value = 'Failed to retrieve employee information.'
      errorMessage.value = 'Could not retrieve operator information.'
    }
  } catch (error) {
    console.error('Master data fetch error:', error)
    errorMessage.value = 'Failed to retrieve master data'
  }
}

const fetchRecentTraces = async () => {
  try {
    const response = await api.get('/trace/stamp-traces?limit=10')
    recentTraces.value = response.data
  } catch (error) {
    console.error('Trace history fetch error:', error)
  }
}

onMounted(async () => {
  await fetchMasterData()
  await fetchRecentTraces()
})
</script>

<style scoped>
.trace-view {
  max-width: 1200px;
  margin: 0 auto;
}

.trace-header {
  margin-bottom: 30px;
}

.trace-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: var(--text-primary);
}

.trace-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.form-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.trace-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: #e74c3c;
}

.form-control {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-control.error-field {
  border-color: #e74c3c;
  background-color: #fdf2f2;
}

.error-text {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-primary:disabled {
  background: var(--border);
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--background-hover);
}

.alert {
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.recent-traces {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.recent-traces h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: var(--text-primary);
  border-bottom: 2px solid var(--primary);
  padding-bottom: 8px;
}

.table-container {
  overflow-x: auto;
  margin-top: 16px;
}

.trace-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.trace-table th {
  background-color: var(--background-secondary);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border);
  white-space: nowrap;
}

.trace-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
}

.trace-table td.number {
  text-align: right;
  font-weight: 500;
}

.trace-table tbody tr:hover {
  background-color: var(--background-hover);
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background-color: #d4edda;
  color: #155724;
}

.badge-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-warning {
  background-color: #fff3cd;
  color: #856404;
}
</style>
