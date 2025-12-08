<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <h1 class="page-title">販売 - PO管理</h1>

      <!-- 一括登録 -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>一括登録（Excel貼り付け）</h2>
        <ClipboardImport @import-success="handleImportSuccess" />
      </div>

      <!-- PO登録フォーム -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>{{ editMode ? 'PO編集' : 'PO登録' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">PO番号</label>
              <input v-model="form.po_number" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">製品コード</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="code"
                value-field="id"
                placeholder="製品コードを入力..."
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">数量</label>
              <input v-model.number="form.po_quantity" class="form-input" type="number" required />
            </div>
            <div style="width: 143px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">納期</label>
              <input v-model="form.delivery_date" class="form-input" type="date" required />
            </div>
            <div style="width: 143px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">PO受取日</label>
              <input v-model="form.date_receive_po" class="form-input" type="date" required />
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="submit" class="btn btn-primary">{{ editMode ? '更新' : '登録' }}</button>
              <button v-if="editMode" @click="cancelEdit" type="button" class="btn btn-secondary">キャンセル</button>
              <button v-if="editMode" @click="handleDelete" type="button" class="btn btn-danger">削除</button>
              <button @click="calculateDeliveryDate" type="button" class="btn btn-success">📅 納期計算</button>
            </div>
          </div>
        </form>

        <!-- 納期計算結果 -->
        <div v-if="deliveryCalculation" style="margin-top: var(--spacing-md); padding: var(--spacing-md); background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
          <h3 style="margin-bottom: var(--spacing-sm); color: #2e7d32;">📊 納期計算結果</h3>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-sm); margin-bottom: var(--spacing-md);">
            <div>
              <strong>開始日:</strong> {{ formatDateForDisplay(deliveryCalculation.start_date) }}
            </div>
            <div>
              <strong>計算納期:</strong> <span style="color: #1976d2; font-weight: 600;">{{ formatDateForDisplay(deliveryCalculation.delivery_date) }}</span>
            </div>
            <div>
              <strong>総所要日数:</strong> {{ deliveryCalculation.total_days }}営業日
            </div>
            <div>
              <strong>PO数量:</strong> {{ deliveryCalculation.po_quantity.toLocaleString() }}個
            </div>
          </div>

          <!-- 工程詳細 -->
          <h4 style="margin-bottom: var(--spacing-sm);">工程詳細</h4>
          <div style="overflow-x: auto;">
            <table class="table" style="background: white;">
              <thead>
                <tr>
                  <th>工程No.</th>
                  <th>工程名</th>
                  <th>タイプ</th>
                  <th>所要日数</th>
                  <th>開始日</th>
                  <th>完了日</th>
                  <th>DAY/CT</th>
                  <th>生産限界</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="process in deliveryCalculation.processes" :key="process.process_no">
                  <td>{{ process.process_no }}</td>
                  <td>{{ process.process_name }}</td>
                  <td>
                    <span :style="{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.85rem',
                      fontWeight: '600',
                      background: process.process_type === 'DAY' ? '#e3f2fd' : '#fff3e0',
                      color: process.process_type === 'DAY' ? '#1976d2' : '#f57c00'
                    }">
                      {{ process.process_type }}
                    </span>
                  </td>
                  <td>{{ process.days }}日</td>
                  <td>{{ formatDateForDisplay(process.start_date) }}</td>
                  <td>{{ formatDateForDisplay(process.end_date) }}</td>
                  <td>{{ process.rough_cycletime || '-' }}</td>
                  <td>{{ process.production_limit ? process.production_limit.toLocaleString() : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style="margin-top: var(--spacing-sm);">
            <button @click="applyCalculatedDate" class="btn btn-primary btn-sm">計算された納期を適用</button>
            <button @click="deliveryCalculation = null" class="btn btn-secondary btn-sm" style="margin-left: var(--spacing-sm);">閉じる</button>
          </div>
        </div>
      </div>

      <!-- PO一覧 -->
      <div class="card">
        <h2>PO一覧</h2>

        <!-- 検索フィールド -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md); flex-wrap: wrap;">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">PO番号</label>
            <input
              v-model="searchFilters.po_number"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="PO番号で検索..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">顧客名</label>
            <input
              v-model="searchFilters.customer_name"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="顧客名で検索..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0; font-size: 0.85rem;">製品コード</label>
            <input
              v-model="searchFilters.product_code"
              @input="handleSearch"
              class="form-input"
              type="text"
              placeholder="製品コードで検索..."
              style="font-size: 0.9rem;"
            />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button
              @click="clearSearch"
              class="btn btn-secondary"
              style="padding: 8px 16px; font-size: 0.9rem;"
            >
              クリア
            </button>
          </div>
        </div>

        <table class="table">
          <thead>
            <tr>
              <th>PO番号</th>
              <th>顧客名</th>
              <th>製品コード</th>
              <th>数量</th>
              <th>納期</th>
              <th>PO受取日</th>
              <th>登録日時</th>
              <th>登録者</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="po in poList" :key="po.po_id">
              <td>{{ po.po_number }}</td>
              <td>{{ po.customer_name || '-' }}</td>
              <td>
                <CopyableText v-if="po.product_code" :text="po.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ po.po_quantity.toLocaleString() }}</td>
              <td>{{ formatDateForDisplay(po.delivery_date) }}</td>
              <td>{{ formatDateForDisplay(po.date_receive_po) }}</td>
              <td>{{ formatTimestamp(po.timestamp) }}</td>
              <td>{{ po.user || '-' }}</td>
              <td>
                <button @click="editPO(po)" class="btn btn-sm btn-secondary">編集</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="poList.length === 0" class="empty-state">
          <p>POデータがありません</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../components/common/AppHeader.vue'
import AppNavigation from '../components/common/AppNavigation.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import ClipboardImport from '../components/sales/ClipboardImport.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../utils/dateFormat'

const editMode = ref(false)
const editingPoId = ref(null)

const form = ref({
  po_number: '',
  product_id: null,
  po_quantity: null,
  delivery_date: '',
  date_receive_po: new Date().toISOString().split('T')[0], // YYYY-MM-DD format for type="date"
})

const poList = ref([])
const searchFilters = ref({
  po_number: '',
  customer_name: '',
  product_code: ''
})

// 納期計算
const deliveryCalculation = ref(null)

let searchTimeout = null

const loadPOs = async () => {
  try {
    const params = {}

    if (searchFilters.value.po_number) {
      params.po_number = searchFilters.value.po_number
    }
    if (searchFilters.value.customer_name) {
      params.customer_name = searchFilters.value.customer_name
    }
    if (searchFilters.value.product_code) {
      params.product_code = searchFilters.value.product_code
    }

    const response = await api.get('/sales/po', { params })
    poList.value = response.data
  } catch (error) {
    console.error('Failed to load POs:', error)
  }
}

const handleSearch = () => {
  // デバウンス処理（入力後300ms待ってから検索）
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadPOs()
  }, 300)
}

const clearSearch = () => {
  searchFilters.value = {
    po_number: '',
    customer_name: '',
    product_code: ''
  }
  loadPOs()
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('製品コードを選択してください')
    return
  }

  try {
    if (editMode.value) {
      // 更新
      await api.put(`/sales/po/${editingPoId.value}`, form.value)
      alert('PO更新成功')
      cancelEdit()
    } else {
      // 新規登録
      await api.post('/sales/po', form.value)
      alert('PO登録成功')
      form.value = {
        po_number: '',
        product_id: null,
        po_quantity: null,
        delivery_date: '',
        date_receive_po: new Date().toISOString().split('T')[0],
      }
    }
    loadPOs()
  } catch (error) {
    console.error('Failed to save PO:', error)
    alert(editMode.value ? 'PO更新失敗' : 'PO登録失敗')
  }
}

const editPO = (po) => {
  editMode.value = true
  editingPoId.value = po.po_id
  form.value = {
    po_number: po.po_number,
    product_id: po.product_id,
    po_quantity: po.po_quantity,
    delivery_date: po.delivery_date,
    date_receive_po: po.date_receive_po,
  }
  // 画面をスクロールしてフォームを表示
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  editMode.value = false
  editingPoId.value = null
  form.value = {
    po_number: '',
    product_id: null,
    po_quantity: null,
    delivery_date: '',
    date_receive_po: new Date().toISOString().split('T')[0],
  }
}

const handleDelete = async () => {
  if (!confirm('このPOを削除しますか？')) {
    return
  }

  try {
    await api.delete(`/sales/po/${editingPoId.value}`)
    alert('PO削除成功')
    cancelEdit()
    loadPOs()
  } catch (error) {
    console.error('Failed to delete PO:', error)
    alert('PO削除失敗')
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}`
}

const calculateDeliveryDate = async () => {
  // バリデーション
  if (!form.value.product_id) {
    alert('製品コードを選択してください')
    return
  }
  if (!form.value.po_quantity || form.value.po_quantity <= 0) {
    alert('数量を入力してください')
    return
  }
  if (!form.value.date_receive_po) {
    alert('PO受取日を入力してください')
    return
  }

  try {
    const response = await api.post('/sales/po/calculate-delivery', {
      product_id: form.value.product_id,
      po_quantity: form.value.po_quantity,
      start_date: form.value.date_receive_po
    })
    deliveryCalculation.value = response.data
    console.log('Delivery calculation result:', response.data)
  } catch (error) {
    console.error('Failed to calculate delivery date:', error)
    alert('納期計算に失敗しました: ' + (error.response?.data?.detail || error.message))
  }
}

const applyCalculatedDate = () => {
  if (deliveryCalculation.value && deliveryCalculation.value.delivery_date) {
    form.value.delivery_date = deliveryCalculation.value.delivery_date
    alert('計算された納期を適用しました')
  }
}

const handleImportSuccess = () => {
  loadPOs()
}

onMounted(() => {
  loadPOs()
})
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

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.85rem;
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}
</style>
