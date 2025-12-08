<template>
  <div class="csv-upload-container">
    <!-- ドラッグ&ドロップエリア -->
    <div
      v-if="!validatedData"
      class="dropzone"
      :class="{ 'dropzone-active': isDragging }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
    >
      <div class="dropzone-content">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <p class="dropzone-text">CSVファイルをドラッグ&ドロップ</p>
        <p class="dropzone-subtext">または</p>
        <button type="button" class="btn btn-secondary" @click="triggerFileInput">
          ファイルを選択
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".csv"
          style="display: none"
          @change="handleFileSelect"
        />
      </div>
      <div class="csv-format-hint">
        <p><strong>CSVフォーマット（ヘッダー行なし、6カラム固定）:</strong></p>
        <div class="format-example">
          <div class="format-header">
            <span>1列目</span>
            <span>2列目</span>
            <span>3列目</span>
            <span>4列目</span>
            <span>5列目</span>
            <span>6列目</span>
          </div>
          <div class="format-fields">
            <span>PO番号</span>
            <span>製品コード</span>
            <span>顧客名</span>
            <span>数量</span>
            <span>PO受取日</span>
            <span>納期</span>
          </div>
          <code>po001,xx001,TOYOTA,500,10/11/2025,15/11/2025</code>
        </div>
        <p style="margin-top: var(--spacing-sm); font-size: 0.85rem; color: var(--text-secondary);">
          ※ ヘッダー行は不要です。1行目からデータを入力してください。<br>
          ※ 日付形式: <strong>DD/MM/YYYY</strong>（例: 10/11/2025 = 2025年11月10日）
        </p>
      </div>
    </div>

    <!-- ローディング -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>CSVを処理中...</p>
    </div>

    <!-- プレビューテーブル -->
    <div v-if="validatedData && !isLoading" class="preview-container">
      <div class="preview-header">
        <h3>データプレビュー</h3>
        <div class="preview-stats">
          <span class="stat">
            全体: <strong>{{ validatedData.total_rows }}</strong>行
          </span>
          <span class="stat stat-error" v-if="errorRowCount > 0">
            エラー: <strong>{{ errorRowCount }}</strong>行
          </span>
          <span class="stat stat-success" v-else>
            エラーなし ✓
          </span>
        </div>
      </div>

      <div v-if="errorRowCount > 0" class="edit-hint">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        エラーのあるセルをクリックして編集できます。編集後は自動的に再検証されます。
      </div>

      <div class="table-wrapper">
        <table class="preview-table">
          <thead>
            <tr>
              <th>#</th>
              <th>PO番号</th>
              <th>製品コード</th>
              <th>顧客名</th>
              <th>数量</th>
              <th>PO受取日</th>
              <th>納期</th>
              <th>状態</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, index) in validatedData.data"
              :key="row.row_number"
              :class="{ 'row-error': row.has_errors }"
            >
              <td>{{ row.row_number }}</td>
              <td :class="{ 'cell-error': row.errors?.po_number }">
                <input
                  v-model="row.po_number"
                  class="cell-input"
                  @input="handleCellEdit(index, 'po_number')"
                />
                <span v-if="row.errors?.po_number" class="error-tooltip">
                  {{ row.errors.po_number }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.product_code }">
                <input
                  v-model="row.product_code"
                  class="cell-input"
                  @input="handleCellEdit(index, 'product_code')"
                />
                <span v-if="row.errors?.product_code" class="error-tooltip">
                  {{ row.errors.product_code }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.customer_name }">
                <input
                  v-model="row.customer_name"
                  class="cell-input"
                  @input="handleCellEdit(index, 'customer_name')"
                />
                <span v-if="row.errors?.customer_name" class="error-tooltip">
                  {{ row.errors.customer_name }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.po_quantity }">
                <input
                  v-model="row.po_quantity"
                  class="cell-input"
                  type="text"
                  @input="handleCellEdit(index, 'po_quantity')"
                />
                <span v-if="row.errors?.po_quantity" class="error-tooltip">
                  {{ row.errors.po_quantity }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.date_receive_po }">
                <input
                  v-model="row.date_receive_po"
                  class="cell-input"
                  @input="handleCellEdit(index, 'date_receive_po')"
                />
                <span v-if="row.errors?.date_receive_po" class="error-tooltip">
                  {{ row.errors.date_receive_po }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.delivery_date }">
                <input
                  v-model="row.delivery_date"
                  class="cell-input"
                  @input="handleCellEdit(index, 'delivery_date')"
                />
                <span v-if="row.errors?.delivery_date" class="error-tooltip">
                  {{ row.errors.delivery_date }}
                </span>
              </td>
              <td>
                <span v-if="row.has_errors" class="badge badge-error">エラー</span>
                <span v-else class="badge badge-success">OK</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="preview-actions">
        <button type="button" class="btn btn-secondary" @click="resetUpload">
          キャンセル
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="handleImport"
          :disabled="errorRowCount > 0 || isImporting"
        >
          {{ isImporting ? '登録中...' : `${validatedData.total_rows - errorRowCount}件を登録` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../../utils/api'

const emit = defineEmits(['import-success'])

const isDragging = ref(false)
const isLoading = ref(false)
const isImporting = ref(false)
const validatedData = ref(null)
const fileInput = ref(null)
const revalidateDebounce = ref(null)

// エラー行数を動的に計算
const errorRowCount = computed(() => {
  if (!validatedData.value) return 0
  return validatedData.value.data.filter(row => row.has_errors).length
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    uploadFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  if (file && file.name.endsWith('.csv')) {
    uploadFile(file)
  } else {
    alert('CSVファイルのみアップロード可能です')
  }
}

const uploadFile = async (file) => {
  isLoading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/sales/po/csv/validate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    validatedData.value = response.data
  } catch (error) {
    console.error('Failed to validate CSV:', error)
    alert(error.response?.data?.detail || 'CSVのアップロードに失敗しました')
  } finally {
    isLoading.value = false
  }
}

const handleCellEdit = (rowIndex, fieldName) => {
  // デバウンスを使って編集後に自動再検証
  if (revalidateDebounce.value) {
    clearTimeout(revalidateDebounce.value)
  }

  revalidateDebounce.value = setTimeout(() => {
    revalidateRow(rowIndex)
  }, 500)
}

const revalidateRow = async (rowIndex) => {
  const row = validatedData.value.data[rowIndex]
  const errors = {}

  // 1. 必須フィールドチェック
  const required_fields = ['po_number', 'product_code', 'customer_name', 'po_quantity', 'date_receive_po', 'delivery_date']
  for (const field of required_fields) {
    if (!row[field] || !row[field].toString().trim()) {
      errors[field] = `${field}が空です`
    }
  }

  // 2. 製品コードと顧客名の検証（サーバー側でチェック）
  try {
    // 簡易的なクライアント側検証
    // 数量の検証
    if (row.po_quantity) {
      const quantity = parseInt(row.po_quantity)
      if (isNaN(quantity) || quantity <= 0) {
        errors.po_quantity = "数量は1以上の整数である必要があります"
      } else {
        row.po_quantity_int = quantity
      }
    }

    // 日付の簡易検証
    const dateFields = ['date_receive_po', 'delivery_date']
    for (const field of dateFields) {
      if (row[field]) {
        const dateStr = row[field].toString().trim()
        // 簡易的な日付フォーマットチェック
        const datePatterns = [
          /^\d{4}-\d{2}-\d{2}$/,  // YYYY-MM-DD
          /^\d{1,2}\/\d{1,2}\/\d{4}$/,  // MM/DD/YYYY or DD/MM/YYYY
          /^\d{4}\/\d{2}\/\d{2}$/  // YYYY/MM/DD
        ]

        const isValidFormat = datePatterns.some(pattern => pattern.test(dateStr))
        if (!isValidFormat) {
          errors[field] = "日付形式が不正です（YYYY-MM-DD, MM/DD/YYYY等）"
        }
      }
    }
  } catch (e) {
    console.error('Validation error:', e)
  }

  // エラーを更新
  row.errors = errors
  row.has_errors = Object.keys(errors).length > 0
}

const handleImport = async () => {
  if (!validatedData.value || errorRowCount.value > 0) {
    return
  }

  isImporting.value = true

  try {
    const response = await api.post('/sales/po/csv/import', validatedData.value.data)
    alert(response.data.message)
    emit('import-success')
    resetUpload()
  } catch (error) {
    console.error('Failed to import CSV:', error)
    alert(error.response?.data?.detail || 'CSV一括登録に失敗しました')
  } finally {
    isImporting.value = false
  }
}

const resetUpload = () => {
  validatedData.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.csv-upload-container {
  width: 100%;
}

.dropzone {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-xl);
  text-align: center;
  transition: all 0.3s ease;
  background: var(--bg-secondary);
}

.dropzone:hover,
.dropzone-active {
  border-color: var(--primary-color);
  background: var(--bg-hover);
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--text-secondary);
}

.dropzone-content svg {
  color: var(--text-secondary);
}

.dropzone-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: var(--text-primary);
}

.dropzone-subtext {
  margin: 0;
  font-size: 0.9rem;
}

.csv-format-hint {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  text-align: left;
}

.csv-format-hint p {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: 0.9rem;
}

.format-example {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: var(--spacing-sm);
}

.format-header,
.format-fields {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
  font-size: 0.75rem;
}

.format-header {
  color: var(--text-secondary);
  font-weight: 600;
}

.format-header span,
.format-fields span {
  padding: 4px 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  text-align: center;
}

.format-fields {
  font-weight: 500;
  color: var(--primary-color);
}

.csv-format-hint code {
  display: block;
  padding: var(--spacing-sm);
  background: #f0f8ff;
  border: 1px solid #d0e8ff;
  border-radius: 4px;
  font-size: 0.85rem;
  overflow-x: auto;
  margin-top: 4px;
}

.loading {
  text-align: center;
  padding: var(--spacing-xl);
}

.spinner {
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-container {
  width: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.preview-header h3 {
  margin: 0;
}

.preview-stats {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.stat {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  font-size: 0.9rem;
}

.stat-error {
  background: #fee;
  color: #c44;
}

.stat-success {
  background: #efe;
  color: #4a4;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.preview-table th {
  background: var(--bg-secondary);
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 2px solid var(--border-color);
  font-weight: 600;
  position: sticky;
  top: 0;
}

.preview-table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
  position: relative;
}

.row-error {
  background: #fff5f5;
}

.cell-error {
  background: #fdd;
  color: #c44;
  font-weight: 500;
}

.error-tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 0;
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 10;
  margin-bottom: 4px;
}

.cell-error:hover .error-tooltip {
  display: block;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-error {
  background: #fdd;
  color: #c44;
}

.badge-success {
  background: #dfd;
  color: #4a4;
}

.preview-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

.edit-hint {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: #e8f4fd;
  border-left: 3px solid #0078d4;
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
  font-size: 0.9rem;
  color: #004578;
}

.edit-hint svg {
  flex-shrink: 0;
  color: #0078d4;
}

.cell-input {
  width: 100%;
  padding: 4px 6px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 0.9rem;
  background: transparent;
  transition: all 0.2s ease;
}

.cell-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.1);
}

.cell-error .cell-input {
  background: #fdd;
  border-color: #faa;
}

.cell-error .cell-input:focus {
  background: white;
  border-color: #c44;
  box-shadow: 0 0 0 2px rgba(204, 68, 68, 0.1);
}
</style>
