<template>
  <AppLayout>
      <div class="trace-view">
        <div class="trace-header">
          <h1>委託記録登録</h1>
          <p class="trace-subtitle">委託作業のトレース情報を登録</p>
        </div>

        <!-- 登録フォーム -->
        <div class="form-section">
          <form @submit.prevent="submitTrace" class="trace-form">
            <div class="form-row">
              <div class="form-group">
                <label for="product-code">プロダクトコード <span class="required">*</span></label>
                <AutocompleteInput
                  v-model="form.product_code"
                  endpoint="/master/autocomplete/products"
                  display-field="product_code"
                  value-field="product_code"
                  placeholder="例: P-12345"
                  required
                  @select="onProductSelect"
                />
              </div>

              <div class="form-group">
                <label for="customer-name">顧客名</label>
                <input
                  id="customer-name"
                  v-model="customerName"
                  type="text"
                  class="form-control"
                  readonly
                  placeholder="プロダクトコード入力後に自動表示"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="lot-number">ロット番号 <span class="required">*</span></label>
                <input
                  id="lot-number"
                  v-model="form.lot_number"
                  type="text"
                  class="form-control"
                  placeholder="例: SECC 120923 JFE"
                  required
                >
              </div>

              <div class="form-group">
                <label for="process">工程 <span class="required">*</span></label>
                <select id="process" v-model="form.process_id" class="form-control" required>
                  <option value="">選択してください</option>
                  <option v-for="process in filteredProcesses" :key="process.process_id" :value="process.process_id">
                    {{ process.process_name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="supplier-name">委託先 <span class="required">*</span></label>
                <AutocompleteInput
                  v-model="form.supplier_id"
                  endpoint="/master/suppliers"
                  display-field="supplier_name"
                  value-field="supplier_id"
                  placeholder="例: 株式会社ABC"
                  required
                  @select="onSupplierSelect"
                />
              </div>

              <div class="form-group">
                <label for="date">作業日 <span class="required">*</span></label>
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
                <label for="ok-quantity">OK数量 <span class="required">*</span></label>
                <input
                  id="ok-quantity"
                  v-model.number="form.ok_quantity"
                  type="number"
                  min="0"
                  class="form-control"
                  placeholder="数量を入力してください"
                  required
                >
              </div>

              <div class="form-group">
                <label for="ng-quantity">NG数量 <span class="required">*</span></label>
                <input
                  id="ng-quantity"
                  v-model.number="form.ng_quantity"
                  type="number"
                  min="0"
                  class="form-control"
                  placeholder="数量を入力してください"
                  required
                >
              </div>
            </div>

            <div class="form-group full-width">
              <label for="note">備考</label>
              <textarea
                id="note"
                v-model="form.note"
                class="form-control"
                rows="3"
                placeholder="備考を入力してください"
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="button" @click="resetForm" class="btn btn-secondary">
                クリア
              </button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitDisabled">
                {{ submitting ? '登録中...' : '登録' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 成功/エラーメッセージ -->
        <div v-if="successMessage" class="alert alert-success">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="alert alert-error">
          {{ errorMessage }}
        </div>

        <!-- 登録済みトレース履歴 -->
        <div v-if="recentTraces.length > 0" class="recent-traces">
          <h2>最近の登録履歴</h2>
          <div class="table-container">
            <table class="trace-table">
              <thead>
                <tr>
                  <th>登録日時</th>
                  <th>製品番号</th>
                  <th>ロット番号</th>
                  <th>工程名</th>
                  <th>委託先</th>
                  <th>OK数量</th>
                  <th>NG数量</th>
                  <th>備考</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trace in recentTraces" :key="trace.outsource_trace_id">
                  <td>{{ formatDateTime(trace.timestamp) }}</td>
                  <td>{{ trace.product_code || '-' }}</td>
                  <td>{{ trace.lot_number || '-' }}</td>
                  <td>{{ trace.process_name || '-' }}</td>
                  <td>{{ trace.supplier_name || '-' }}</td>
                  <td class="number">{{ trace.ok_quantity }}</td>
                  <td class="number">{{ trace.ng_quantity }}</td>
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

// フォーム
const form = ref({
  product_code: '',
  product_id: null,
  lot_number: '',
  process_id: '',
  supplier_id: null,
  supplier_name: '',
  ok_quantity: null,
  ng_quantity: null,
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
         !form.value.supplier_id ||
         form.value.ok_quantity === null ||
         form.value.ng_quantity === null
})

// イベントハンドラ
const onProductSelect = (product) => {
  if (product) {
    form.value.product_id = product.id
    customerName.value = product.customer_name || ''
    form.value.process_id = ''
  } else {
    form.value.product_code = ''
    customerName.value = ''
    form.value.product_id = null
    form.value.process_id = ''
  }
}

const onSupplierSelect = (supplier) => {
  if (supplier) {
    form.value.supplier_name = supplier.supplier_name
  } else {
    form.value.supplier_name = ''
  }
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

const resetForm = () => {
  // 登録後も保持する項目
  const currentProductCode = form.value.product_code
  const currentProductId = form.value.product_id
  const currentLotNumber = form.value.lot_number
  const currentProcessId = form.value.process_id
  const currentSupplierId = form.value.supplier_id
  const currentSupplierName = form.value.supplier_name

  form.value = {
    product_code: currentProductCode,
    product_id: currentProductId,
    lot_number: currentLotNumber,
    process_id: currentProcessId,
    supplier_id: currentSupplierId,
    supplier_name: currentSupplierName,
    ok_quantity: null,
    ng_quantity: null,
    date: new Date().toISOString().split('T')[0],
    note: ''
  }
  // customerNameは保持
  successMessage.value = ''
  errorMessage.value = ''
}

const submitTrace = async () => {
  // バリデーション
  if (!form.value.product_id) {
    errorMessage.value = '製品コードを入力してください'
    return
  }

  if (!form.value.lot_number || form.value.lot_number.trim() === '') {
    errorMessage.value = 'ロット番号を入力してください'
    return
  }

  if (!form.value.process_id) {
    errorMessage.value = '工程を選択してください'
    return
  }

  if (!form.value.supplier_id) {
    errorMessage.value = '委託先を選択してください'
    return
  }

  if (form.value.ok_quantity === null || form.value.ok_quantity === '') {
    errorMessage.value = 'OK数量を入力してください'
    return
  }

  if (form.value.ng_quantity === null || form.value.ng_quantity === '') {
    errorMessage.value = 'NG数量を入力してください'
    return
  }

  submitting.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    // 委託トレースを登録
    await api.post('/trace/outsource-trace-simple', {
      product_id: form.value.product_id,
      lot_number: form.value.lot_number,
      process_id: form.value.process_id,
      supplier_name: form.value.supplier_name,
      ok_quantity: form.value.ok_quantity,
      ng_quantity: form.value.ng_quantity,
      date: form.value.date,
      note: form.value.note
    })

    successMessage.value = '委託記録を登録しました'
    resetForm()
    await fetchRecentTraces()
  } catch (error) {
    console.error('トレース登録エラー:', error)
    errorMessage.value = error.response?.data?.detail || 'トレース登録に失敗しました'
  } finally {
    submitting.value = false
  }
}

const fetchMasterData = async () => {
  try {
    // 工程一覧を取得
    const processResponse = await api.get('/process/list')
    processList.value = processResponse.data
  } catch (error) {
    console.error('マスタデータ取得エラー:', error)
    errorMessage.value = 'マスタデータの取得に失敗しました'
  }
}

const fetchRecentTraces = async () => {
  try {
    const response = await api.get('/trace/outsource-traces?limit=10')
    recentTraces.value = response.data
  } catch (error) {
    console.error('トレース履歴取得エラー:', error)
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
</style>
