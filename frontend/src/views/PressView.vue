<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <h1 class="page-title">プレス - 工程管理</h1>

      <!-- 工程登録フォーム -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editMode ? '工程編集' : '工程登録' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">製品コード</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="product_code"
                value-field="id"
                placeholder="製品コードを入力..."
                @select="handleProductSelect"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">工程番号</label>
              <input v-model.number="form.process_no" class="form-input" type="number" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">工程名</label>
              <AutocompleteInput
                v-model="form.process_name"
                endpoint="/press/autocomplete/process-names"
                display-field="process_name"
                value-field="process_name"
                placeholder="工程名を選択..."
                @select="handleProcessNameSelect"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">{{ cycleTimeLabel }}</label>
              <input v-model.number="form.rough_cycletime" class="form-input" type="number" step="0.01" />
            </div>
            <div v-if="processType === true" style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">段取時間（min）</label>
              <input v-model.number="form.setup_time" class="form-input" type="number" step="0.01" />
            </div>
            <div v-if="processType === false" style="width: 100px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">生産可能限界（PCS）</label>
              <input v-model.number="form.production_limit" class="form-input" type="number" />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">{{ editMode ? '更新' : '登録' }}</button>
              <button v-if="editMode" @click="cancelEdit" type="button" class="btn btn-secondary">キャンセル</button>
              <button v-if="editMode" @click="handleDelete" type="button" class="btn btn-danger">削除</button>
            </div>
          </div>
        </form>

        <!-- 選択された製品の工程表 -->
        <div v-if="selectedProductProcess" style="margin-top: var(--spacing-lg);">
          <h3 style="margin-bottom: var(--spacing-sm); color: var(--primary);">
            {{ selectedProductProcess.customer_name }} -
            <CopyableText :text="selectedProductProcess.product_code" />
          </h3>
          <div class="table-scroll-container">
            <table class="table process-table">
              <thead>
                <tr>
                  <th v-for="i in 20" :key="i">工程{{ i }}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td
                    v-for="i in 20"
                    :key="i"
                    :class="{ 'clickable-cell': selectedProductProcess[`process_${i}`] }"
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

      <!-- タブナビゲーション -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'process-table'"
          :class="{ active: activeTab === 'process-table' }"
          class="tab-btn"
        >
          工程表
        </button>
        <button
          @click="activeTab = 'process-list'"
          :class="{ active: activeTab === 'process-list' }"
          class="tab-btn"
        >
          工程一覧（データベース）
        </button>
      </div>

      <!-- 工程表タブ -->
      <div v-if="activeTab === 'process-table'" class="card">
        <h2>工程表</h2>

        <!-- 検索フィールド -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">顧客名</label>
            <input v-model="searchTable.customer_name" class="form-input" type="text" placeholder="顧客名で検索..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">製品コード</label>
            <input v-model="searchTable.product_code" class="form-input" type="text" placeholder="製品コードで検索..." />
          </div>
        </div>

        <div class="table-scroll-container">
          <table class="table process-table">
            <thead>
              <tr>
                <th class="sticky-col">顧客名</th>
                <th class="sticky-col-2">製品コード</th>
                <th v-for="i in 20" :key="i">工程{{ i }}</th>
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
                  :class="{ 
                    'clickable-cell': product[`process_${i}`],
                    'error-cell': isPressSetIncomplete(product, product[`process_${i}`])
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
          <p>工程データがありません</p>
        </div>
      </div>

      <!-- 工程一覧タブ -->
      <div v-if="activeTab === 'process-list'" class="card">
        <h2>工程一覧（データベース）</h2>

        <!-- 検索フィールド -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">顧客名</label>
            <input v-model="searchList.customer_name" class="form-input" type="text" placeholder="顧客名で検索..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">製品コード</label>
            <input v-model="searchList.product_code" class="form-input" type="text" placeholder="製品コードで検索..." />
          </div>
        </div>

        <table class="table">
          <thead>
            <tr>
              <th>登録日時</th>
              <th>顧客名</th>
              <th>製品コード</th>
              <th class="sortable-header" @click="toggleSort('process_no')">
                工程番号 <span class="sort-icon">{{ getSortIcon('process_no') }}</span>
              </th>
              <th>工程名</th>
              <th>サイクルタイム</th>
              <th>段取時間（min）</th>
              <th>生産可能限界（PCS）</th>
              <th>操作</th>
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
                <button @click="editProcess(process)" class="btn btn-sm btn-secondary">編集</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="filteredProcessList.length === 0" class="empty-state">
          <p>工程データがありません</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppHeader from '../components/common/AppHeader.vue'
import AppNavigation from '../components/common/AppNavigation.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'

const activeTab = ref('process-table')
const editMode = ref(false)
const editingProcessId = ref(null)
const processType = ref(null) // null: デフォルト, true: SPM, false: DAY
const cycleTimeLabel = ref('サイクルタイム')

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

const processList = ref([])
const processTable = ref([])
const processNameSuggestions = ref([])

// 工程表フィルタリング
const filteredProcessTable = computed(() => {
  return processTable.value.filter(product => {
    const customerMatch = !searchTable.value.customer_name ||
      product.customer_name.toLowerCase().includes(searchTable.value.customer_name.toLowerCase())
    const productMatch = !searchTable.value.product_code ||
      product.product_code.toLowerCase().includes(searchTable.value.product_code.toLowerCase())
    return customerMatch && productMatch
  })
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
    alert('製品コードを選択してください')
    return
  }

  // 工程名がマスターに存在するかチェック
  if (!processNameSuggestions.value.includes(form.value.process_name)) {
    alert('入力された工程名はマスターに登録されていません。\nリストから選択してください。')
    return
  }

  try {
    if (editMode.value) {
      // 更新
      await api.put(`/press/processes/${editingProcessId.value}`, form.value)
      alert('工程更新成功')
      cancelEdit()
    } else {
      // 新規登録
      const currentProductId = form.value.product_id
      await api.post('/press/processes', form.value)
      alert('工程登録成功')
      processType.value = null
      cycleTimeLabel.value = 'サイクルタイム'
      form.value = {
        product_id: currentProductId, // 製品IDを保持
        process_no: null,
        process_name: '',
        rough_cycletime: null,
        setup_time: null,
        production_limit: 99999,
      }
    }
    await loadProcesses()
    await loadProcessTable()
    // 選択されている製品の工程表を更新
    if (form.value.product_id) {
      await handleProductSelect()
    }
  } catch (error) {
    console.error('Failed to save process:', error)
    alert(editMode.value ? '工程更新失敗' : '工程登録失敗')
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
  // 工程名に応じたタイプを取得
  handleProcessNameChange()
  // 画面をスクロールしてフォームを表示
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const editProcessCell = async (product, processNo) => {
  // 工程名がない場合はクリック不可
  if (!product[`process_${processNo}`]) {
    return
  }

  try {
    // 該当する工程データを取得
    const response = await api.get('/press/processes', {
      params: { product_id: product.product_id }
    })
    const processes = response.data
    const targetProcess = processes.find(p => p.process_no === processNo)

    if (targetProcess) {
      editProcess(targetProcess)
      // 製品の工程表を表示
      await handleProductSelect()
    }
  } catch (error) {
    console.error('Failed to load process:', error)
  }
}

const handleProductSelect = async () => {
  if (!form.value.product_id) {
    selectedProductProcess.value = null
    return
  }

  try {
    // 工程表データから選択された製品の情報を取得
    const response = await api.get('/press/process-table')
    const products = response.data
    const product = products.find(p => p.product_id === form.value.product_id)

    if (product) {
      selectedProductProcess.value = product
    } else {
      selectedProductProcess.value = null
    }
  } catch (error) {
    console.error('Failed to load product process:', error)
  }
}

const editProcessCellFromSearch = async (product, processNo) => {
  // 工程名がない場合はクリック不可
  if (!product[`process_${processNo}`]) {
    return
  }

  try {
    // 該当する工程データを取得
    const response = await api.get('/press/processes', {
      params: { product_id: product.product_id }
    })
    const processes = response.data
    const targetProcess = processes.find(p => p.process_no === processNo)

    if (targetProcess) {
      editProcess(targetProcess)
      // 製品の工程表を表示
      await handleProductSelect()
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
  cycleTimeLabel.value = 'サイクルタイム'
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
  if (!confirm('この工程を削除しますか？')) {
    return
  }

  try {
    const productId = form.value.product_id // 削除前に製品IDを保存
    await api.delete(`/press/processes/${editingProcessId.value}`)
    alert('工程削除成功')
    cancelEdit()
    await loadProcesses()
    await loadProcessTable()
    // 選択されている製品の工程表を更新
    if (productId) {
      form.value.product_id = productId
      await handleProductSelect()
    }
  } catch (error) {
    console.error('Failed to delete process:', error)
    alert('工程削除失敗')
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
</style>
