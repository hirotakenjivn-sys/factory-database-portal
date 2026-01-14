<template>
  <AppLayout>
      <h1 class="page-title">Press - Process Management</h1>

      <!-- Process Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editMode ? 'Edit Process' : 'Register Process' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Product Code</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="product_code"
                value-field="id"
                placeholder="Enter Product Code..."
                @select="handleProductSelect"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Process No</label>
              <input v-model.number="form.process_no" class="form-input" type="number" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Process Name</label>
              <AutocompleteInput
                v-model="form.process_name"
                endpoint="/press/autocomplete/process-names"
                display-field="process_name"
                value-field="process_name"
                placeholder="Select Process Name..."
                @select="handleProcessNameSelect"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">{{ cycleTimeLabel }}</label>
              <input v-model.number="form.rough_cycletime" class="form-input" type="number" step="0.01" />
            </div>
            <div v-if="processType === true" style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Setup Time (min)</label>
              <input v-model.number="form.setup_time" class="form-input" type="number" step="0.01" />
            </div>
            <div v-if="processType === false" style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">Prod. Limit (PCS)</label>
              <input v-model.number="form.production_limit" class="form-input" type="number" />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">{{ editMode ? 'Update' : 'Register' }}</button>
              <button v-if="editMode" @click="cancelEdit" type="button" class="btn btn-secondary">Cancel</button>
              <button v-if="editMode" @click="handleDelete" type="button" class="btn btn-danger">Delete</button>
            </div>
          </div>
        </form>

        <!-- Selected Product Process Table -->
        <div v-if="selectedProductProcess" style="margin-top: var(--spacing-lg);">
          <h3 style="margin-bottom: var(--spacing-sm); color: var(--primary);">
            {{ selectedProductProcess.customer_name }} -
            <CopyableText :text="selectedProductProcess.product_code" />
          </h3>
          <div class="table-scroll-container">
            <table class="table process-table">
              <thead>
                <tr>
                  <th v-for="i in 20" :key="i">Process {{ i }}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td
                    v-for="i in 20"
                    :key="i"
                    class="clickable-cell"
                    :class="{
                      'highlight-zero-cycletime': selectedProductProcess[`process_${i}`] && Number(selectedProductProcess[`rough_cycletime_${i}`]) === 0
                    }"
                    @click="editProcessCellFromSearch(selectedProductProcess, i)"
                  >
                    {{ selectedProductProcess[`process_${i}`] || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'process-table'"
          :class="{ active: activeTab === 'process-table' }"
          class="tab-btn"
        >
          Process Table
        </button>
        <button
          @click="activeTab = 'process-list'"
          :class="{ active: activeTab === 'process-list' }"
          class="tab-btn"
        >
          Process List (Database)
        </button>
      </div>

      <!-- Process Table Tab -->
      <div v-if="activeTab === 'process-table'" class="card">
        <h2>Process Table</h2>

        <!-- Search Fields -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md); align-items: flex-end;">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Customer Name</label>
            <input v-model="searchTable.customer_name" class="form-input" type="text" placeholder="Search Customer..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Product Code</label>
            <input v-model="searchTable.product_code" class="form-input" type="text" placeholder="Search Product Code..." />
          </div>
          <label style="display: flex; align-items: center; gap: 4px; height: 34px;">
            <input v-model="showOnlyHighlighted" type="checkbox" />
            <span>Show only highlighted</span>
          </label>
        </div>

        <div class="table-scroll-container">
          <table class="table process-table">
            <thead>
              <tr>
                <th class="sticky-col">Customer Name</th>
                <th class="sticky-col-2">Product Code</th>
                <th v-for="i in 20" :key="i">Process {{ i }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProcessTable" :key="product.product_id">
                <td class="sticky-col">{{ product.customer_name }}</td>
                <td class="sticky-col-2" @click="selectProductForForm(product)" style="cursor: pointer; color: var(--primary);">
                  {{ product.product_code }}
                </td>
                <td
                  v-for="i in 20"
                  :key="i"
                  class="clickable-cell"
                  :class="{
                    'error-cell': isPressSetIncomplete(product, product[`process_${i}`]),
                    'highlight-zero-cycletime': product[`process_${i}`] && Number(product[`rough_cycletime_${i}`]) === 0
                  }"
                  @click="editProcessCell(product, i)"
                >
                  {{ product[`process_${i}`] || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredProcessTable.length === 0" class="empty-state">
          <p>No process data found</p>
        </div>
      </div>

      <!-- Process List Tab -->
      <div v-if="activeTab === 'process-list'" class="card">
        <h2>Process List (Database)</h2>

        <!-- Search Fields -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Customer Name</label>
            <input v-model="searchList.customer_name" class="form-input" type="text" placeholder="Search Customer..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">Product Code</label>
            <input v-model="searchList.product_code" class="form-input" type="text" placeholder="Search Product Code..." />
          </div>
        </div>

        <table class="table">
          <thead>
            <tr>
              <th>Registered Date</th>
              <th>Customer Name</th>
              <th>Product Code</th>
              <th class="sortable-header" @click="toggleSort('process_no')">
                Process No <span class="sort-icon">{{ getSortIcon('process_no') }}</span>
              </th>
              <th>Process Name</th>
              <th>Cycle Time</th>
              <th>Setup Time (min)</th>
              <th>Prod. Limit (PCS)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="process in filteredProcessList" :key="process.process_id">
              <td>{{ formatDateTime(process.timestamp) }}</td>
              <td>{{ process.customer_name }}</td>
              <td>
                <CopyableText :text="process.product_code" />
              </td>
              <td>{{ process.process_no }}</td>
              <td>{{ process.process_name }}</td>
              <td>{{ process.rough_cycletime || '-' }}</td>
              <td>{{ process.setup_time || '-' }}</td>
              <td>{{ process.production_limit || '-' }}</td>
              <td>
                <button @click="editProcess(process)" class="btn btn-sm btn-secondary">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="filteredProcessList.length === 0" class="empty-state">
          <p>No process data found</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'

const activeTab = ref('process-table')
const editMode = ref(false)
const editingProcessId = ref(null)
const processType = ref(null) // null: デフォルト, true: SPM, false: DAY
const cycleTimeLabel = ref('Cycle Time')

const selectedProductProcess = ref(null)

const form = ref({
  product_id: null,
  process_no: null,
  process_name: '',
  rough_cycletime: null,
  setup_time: null,
  production_limit: 99999,
})

const searchTable = ref({
  customer_name: '',
  product_code: ''
})

const searchList = ref({
  customer_name: '',
  product_code: ''
})

const sortConfig = ref({
  column: null,
  direction: 'asc' // 'asc' or 'desc'
})

const showOnlyHighlighted = ref(false)

const processList = ref([])
const processTable = ref([])
const processNameSuggestions = ref([])

// ハイライト判定（rough_cycletime=0の工程があるか）
const hasHighlight = (product) => {
  for (let i = 1; i <= 20; i++) {
    if (product[`process_${i}`] && Number(product[`rough_cycletime_${i}`]) === 0) {
      return true
    }
  }
  return false
}

// 工程表フィルタリング・ソート
const filteredProcessTable = computed(() => {
  let result = processTable.value.filter(product => {
    const customerMatch = !searchTable.value.customer_name ||
      product.customer_name.toLowerCase().includes(searchTable.value.customer_name.toLowerCase())
    const productMatch = !searchTable.value.product_code ||
      product.product_code.toLowerCase().includes(searchTable.value.product_code.toLowerCase())
    const highlightMatch = !showOnlyHighlighted.value || hasHighlight(product)
    return customerMatch && productMatch && highlightMatch
  })

  // ハイライトがある行を上にソート
  result.sort((a, b) => {
    const aHas = hasHighlight(a) ? 1 : 0
    const bHas = hasHighlight(b) ? 1 : 0
    return bHas - aHas
  })

  return result
})

// 工程一覧ソート（フィルタリングはバックエンドで実行）
const filteredProcessList = computed(() => {
  let filtered = processList.value

  // ソート適用
  if (sortConfig.value.column) {
    filtered = [...filtered].sort((a, b) => {
      const aVal = a[sortConfig.value.column]
      const bVal = b[sortConfig.value.column]

      let comparison = 0
      if (aVal < bVal) comparison = -1
      if (aVal > bVal) comparison = 1

      return sortConfig.value.direction === 'asc' ? comparison : -comparison
    })
  }

  return filtered
})

const loadProcesses = async () => {
  try {
    const params = {}
    if (searchList.value.customer_name) {
      params.customer_name = searchList.value.customer_name
    }
    if (searchList.value.product_code) {
      params.product_code = searchList.value.product_code
    }
    const response = await api.get('/press/processes', { params })
    processList.value = response.data
  } catch (error) {
    console.error('Failed to load processes:', error)
  }
}

const loadProcessTable = async () => {
  try {
    const response = await api.get('/press/process-table')
    console.log('Process table response:', response.data)
    processTable.value = response.data
    console.log('processTable.value:', processTable.value)
    console.log('filteredProcessTable:', filteredProcessTable.value)
  } catch (error) {
    console.error('Failed to load process table:', error)
  }
}

const loadProcessNames = async () => {
  try {
    const response = await api.get('/press/autocomplete/process-names')
    processNameSuggestions.value = response.data.map(item => item.process_name)
  } catch (error) {
    console.error('Failed to load process names:', error)
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('Please select a Product Code')
    return
  }

  // Check if process name exists in master
  if (!processNameSuggestions.value.includes(form.value.process_name)) {
    alert('The entered Process Name is not registered in the master.\nPlease select from the list.')
    return
  }

  try {
    if (editMode.value) {
      // Update
      await api.put(`/press/processes/${editingProcessId.value}`, form.value)
      alert('Process updated successfully')
      cancelEdit()
    } else {
      // Register
      const currentProductId = form.value.product_id
      await api.post('/press/processes', form.value)
      alert('Process registered successfully')
      processType.value = null
      cycleTimeLabel.value = 'Cycle Time'
      form.value = {
        product_id: currentProductId, // Keep Product ID
        process_no: null,
        process_name: '',
        rough_cycletime: null,
        setup_time: null,
        production_limit: 99999,
      }
    }
    await loadProcesses()
    await loadProcessTable()
    // Update selected product process table
    if (form.value.product_id) {
      await handleProductSelect()
    }
  } catch (error) {
    console.error('Failed to save process:', error)
    alert(editMode.value ? 'Failed to update process' : 'Failed to register process')
  }
}

const editProcess = (process) => {
  editMode.value = true
  editingProcessId.value = process.process_id
  form.value = {
    product_id: process.product_id,
    process_no: process.process_no,
    process_name: process.process_name,
    rough_cycletime: process.rough_cycletime,
    setup_time: process.setup_time,
    production_limit: process.production_limit,
  }
  // Get type based on process name
  handleProcessNameChange()
  // Scroll to top to show form
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const editProcessCell = async (product, processNo) => {
  // プロセス名がない場合は新規登録モードでフォームをフィル
  if (!product[`process_${processNo}`]) {
    editMode.value = false
    editingProcessId.value = null
    processType.value = null
    cycleTimeLabel.value = 'Cycle Time'
    form.value = {
      product_id: product.product_id,
      process_no: processNo,
      process_name: '',
      rough_cycletime: null,
      setup_time: null,
      production_limit: 99999,
    }
    selectedProductProcess.value = product
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  try {
    // Get corresponding process data
    const response = await api.get('/press/processes', {
      params: { product_id: product.product_id }
    })
    const processes = response.data
    const targetProcess = processes.find(p => p.process_no === processNo)

    if (targetProcess) {
      editProcess(targetProcess)
      // Show product process table (直接設定してリセットを回避)
      selectedProductProcess.value = product
    }
  } catch (error) {
    console.error('Failed to load process:', error)
  }
}

const handleProductSelect = async () => {
  // 編集モードの場合、リセット
  if (editMode.value) {
    editMode.value = false
    editingProcessId.value = null
  }

  if (!form.value.product_id) {
    selectedProductProcess.value = null
    return
  }

  // まずキャッシュ済みのprocessTableから検索
  const cachedProduct = processTable.value.find(p => p.product_id === form.value.product_id)
  if (cachedProduct) {
    selectedProductProcess.value = cachedProduct
    return
  }

  // キャッシュにない場合のみAPIを呼ぶ
  try {
    const response = await api.get('/press/process-table')
    processTable.value = response.data
    const product = response.data.find(p => p.product_id === form.value.product_id)
    selectedProductProcess.value = product || null
  } catch (error) {
    console.error('Failed to load product process:', error)
  }
}

const editProcessCellFromSearch = async (product, processNo) => {
  // プロセス名がない場合は新規登録モードでフォームをフィル
  if (!product[`process_${processNo}`]) {
    editMode.value = false
    editingProcessId.value = null
    processType.value = null
    cycleTimeLabel.value = 'Cycle Time'
    form.value = {
      product_id: product.product_id,
      process_no: processNo,
      process_name: '',
      rough_cycletime: null,
      setup_time: null,
      production_limit: 99999,
    }
    return
  }

  try {
    // Get corresponding process data
    const response = await api.get('/press/processes', {
      params: { product_id: product.product_id }
    })
    const processes = response.data
    const targetProcess = processes.find(p => p.process_no === processNo)

    if (targetProcess) {
      editProcess(targetProcess)
      // selectedProductProcessはすでに設定されているのでそのまま
    }
  } catch (error) {
    console.error('Failed to load process:', error)
  }
}

const selectProductForForm = async (product) => {
  form.value.product_id = product.product_id
  await handleProductSelect()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  editMode.value = false
  editingProcessId.value = null
  processType.value = null
  cycleTimeLabel.value = 'Cycle Time'
  form.value = {
    product_id: null,
    process_no: null,
    process_name: '',
    rough_cycletime: null,
    setup_time: null,
    production_limit: 99999,
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this process?')) {
    return
  }

  try {
    const productId = form.value.product_id // Save product ID before deletion
    await api.delete(`/press/processes/${editingProcessId.value}`)
    alert('Process deleted successfully')
    cancelEdit()
    await loadProcesses()
    await loadProcessTable()
    // Update selected product process table
    if (productId) {
      form.value.product_id = productId
      await handleProductSelect()
    }
  } catch (error) {
    console.error('Failed to delete process:', error)
    alert('Failed to delete process')
  }
}

// 工程名選択時の処理
const handleProcessNameSelect = async (item) => {
  if (!item) {
    handleProcessNameChange()
    return
  }
  // AutocompleteInputから渡されるのはオブジェクト全体ではなく、選択された値の場合もあるため確認
  // AutocompleteInputの仕様では @select イベントは item オブジェクトを返す
  form.value.process_name = item.process_name
  handleProcessNameChange()
}

// 工程名変更時の処理
const handleProcessNameChange = async () => {
  if (!form.value.process_name) {
    processType.value = null
    cycleTimeLabel.value = 'サイクルタイム'
    return
  }

  try {
    const response = await api.get(`/press/process-name-type/${encodeURIComponent(form.value.process_name)}`)
    processType.value = response.data.day_or_spm
    cycleTimeLabel.value = response.data.type_label

    // 編集モード時は、データベースから読み込んだ値をそのまま保持
    // 新規登録時のみ、タイプに応じたデフォルト値を設定
    if (!editMode.value) {
      // 新規登録時のみ処理
      if (processType.value === true) {
        // SPMの場合、生産可能限界をクリア、段取時間の初期値を60に設定
        form.value.production_limit = null
        if (form.value.setup_time === null) {
          form.value.setup_time = 60
        }
      } else if (processType.value === false) {
        // DAYの場合、段取時間をクリア、生産可能限界に初期値を設定
        form.value.setup_time = null
        if (form.value.production_limit === null || form.value.production_limit === undefined) {
          form.value.production_limit = 99999
        }
      } else {
        // デフォルトの場合、両方クリア
        form.value.setup_time = null
        form.value.production_limit = 99999
      }
    }
    // editMode.value === true の場合、何もしない（データベースの値をそのまま表示）
  } catch (error) {
    console.error('Failed to get process type:', error)
    processType.value = null
    cycleTimeLabel.value = 'サイクルタイム'
  }
}

// ソート関数
const toggleSort = (column) => {
  if (sortConfig.value.column === column) {
    // 同じ列をクリック：昇順 → 降順 → ソート解除
    if (sortConfig.value.direction === 'asc') {
      sortConfig.value.direction = 'desc'
    } else {
      sortConfig.value.column = null
      sortConfig.value.direction = 'asc'
    }
  } else {
    // 別の列をクリック：その列で昇順
    sortConfig.value.column = column
    sortConfig.value.direction = 'asc'
  }
}

const getSortIcon = (column) => {
  if (sortConfig.value.column !== column) return ''
  return sortConfig.value.direction === 'asc' ? '▲' : '▼'
}

// 日時フォーマット関数
const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}

// 検索フィールドの変更を監視してAPI呼び出し
let searchTimeout = null
watch(searchList, () => {
  // デバウンス: 500ms待ってからAPI呼び出し
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadProcesses()
  }, 500)
}, { deep: true })

onMounted(() => {
  loadProcesses()
  loadProcessTable()
  loadProcessNames()
})

const isPressSetIncomplete = (product, processName) => {
  if (!processName) return false

  // PRESS X/Y の形式かチェック (スペース許容)
  const match = processName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
  if (!match) return false

  const denominator = parseInt(match[2], 10)
  
  // 分母が0以下の場合は不正とみなす（あるいは無視）
  if (denominator <= 0) return true

  // 同じ製品の全工程を確認
  // process_1 〜 process_20 をスキャン
  const existingParts = new Set()
  
  for (let i = 1; i <= 20; i++) {
    const pName = product[`process_${i}`]
    if (pName) {
      const pMatch = pName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
      if (pMatch) {
        const pNum = parseInt(pMatch[1], 10)
        const pDenom = parseInt(pMatch[2], 10)
        // 分母が一致するものだけを対象にする
        if (pDenom === denominator) {
          existingParts.add(pNum)
        }
      }
    }
  }

  // 1 〜 denominator まで全て揃っているかチェック
  for (let i = 1; i <= denominator; i++) {
    if (!existingParts.has(i)) {
      return true // 欠けているものがある
    }
  }

  return false // 全て揃っている
}
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

h2 {
  margin-bottom: var(--spacing-md);
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

.table-scroll-container {
  overflow-x: auto;
  max-width: 100%;
}

.process-table {
  min-width: 1500px;
}

.process-table th,
.process-table td {
  min-width: 100px;
  white-space: nowrap;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: white;
  z-index: 2;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.sticky-col-2 {
  position: sticky;
  left: 120px;
  background: white;
  z-index: 2;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.process-table thead .sticky-col,
.process-table thead .sticky-col-2 {
  background: #f8f9fa;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.clickable-cell {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-cell:hover {
  background-color: #e3f2fd;
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

.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.sortable-header:hover {
  background-color: #e8e8e8;
}

.sort-icon {
  display: inline-block;
  margin-left: 4px;
  font-size: 0.8em;
  color: var(--primary);
}

.error-cell {
  background-color: #ffcccc !important; /* 薄い赤色 */
}

.highlight-zero-cycletime {
  background-color: rgba(255, 235, 59, 0.3) !important; /* 半透明の黄色 */
}
</style>
