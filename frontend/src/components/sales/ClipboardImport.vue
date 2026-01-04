<template>
  <div class="clipboard-import-container">
    <!-- Clipboard Paste Area -->
    <div v-if="!validatedData" class="paste-area-wrapper">
      <p class="paste-hint">Copy data from Excel (Ctrl+C) and paste here (Ctrl+V)</p>

      <div class="table-preview">
        <table class="preview-table">
          <thead>
            <tr>
              <th>#</th>
              <th>PO Number</th>
              <th>Product Code</th>
              <th>Customer</th>
              <th>Quantity</th>
              <th>PO Received</th>
              <th>Delivery</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr class="paste-row">
              <td colspan="8" style="padding: 0;">
                <textarea
                  v-model="pastedText"
                  class="paste-textarea-embedded"
                  placeholder="Paste 6-column data from Excel here (Ctrl+V)"
                  @paste="handlePaste"
                ></textarea>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Processing data...</p>
    </div>

    <!-- Preview Table -->
    <div v-if="validatedData && !isLoading" class="preview-container">
      <div class="preview-header">
        <h3>Data Preview</h3>
        <div class="preview-stats">
          <span class="stat">
            Total: <strong>{{ validatedData.total_rows }}</strong> rows
          </span>
          <span class="stat stat-error" v-if="errorRowCount > 0">
            Errors: <strong>{{ errorRowCount }}</strong> rows
          </span>
          <span class="stat stat-success" v-else>
            No errors ✓
          </span>
        </div>
      </div>

      <div v-if="errorRowCount > 0" class="edit-hint">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        Click on cells with errors to edit. Changes are automatically re-validated.
      </div>

      <div class="table-wrapper">
        <table class="preview-table">
          <thead>
            <tr>
              <th>#</th>
              <th>PO Number</th>
              <th>Product Code</th>
              <th>Customer</th>
              <th>Quantity</th>
              <th>PO Received</th>
              <th>Delivery</th>
              <th>Status</th>
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
                <div class="autocomplete-cell">
                  <input
                    v-model="row.product_code"
                    class="cell-input"
                    @input="handleProductCodeInput(index)"
                    @focus="showAutocomplete(index)"
                    @blur="hideAutocomplete(index)"
                    autocomplete="off"
                  />
                  <div
                    v-if="row.showAutocomplete && row.productSuggestions && row.productSuggestions.length > 0"
                    class="autocomplete-dropdown"
                  >
                    <div
                      v-for="suggestion in row.productSuggestions"
                      :key="suggestion.product_id"
                      class="autocomplete-item"
                      @mousedown.prevent="selectProduct(index, suggestion)"
                    >
                      <span class="suggestion-code">{{ suggestion.product_code }}</span>
                      <span class="suggestion-customer">{{ suggestion.customer_name }}</span>
                    </div>
                  </div>
                </div>
                <span v-if="row.errors?.product_code" class="error-tooltip">
                  {{ row.errors.product_code }}
                </span>
              </td>
              <td :class="{ 'cell-error': row.errors?.customer_name }">
                <input
                  v-model="row.customer_name"
                  class="cell-input"
                  :readonly="row.customerAutoFilled"
                  :style="{ background: row.customerAutoFilled ? '#f0f8ff' : '' }"
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
                <span v-if="row.has_errors" class="badge badge-error">Error</span>
                <span v-else class="badge badge-success">OK</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="preview-actions">
        <button type="button" class="btn btn-secondary" @click="resetImport">
          Cancel
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="handleImport"
          :disabled="isImporting || validRowCount === 0"
        >
          {{ isImporting ? 'Registering...' : errorRowCount > 0 ? `Register ${validRowCount} rows (excluding errors)` : `Register ${validRowCount} rows` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../../utils/api'

const emit = defineEmits(['import-success'])

const pastedText = ref('')
const isLoading = ref(false)
const isProcessing = ref(false)
const isImporting = ref(false)
const validatedData = ref(null)
const revalidateDebounce = ref(null)

// Calculate error row count dynamically
const errorRowCount = computed(() => {
  if (!validatedData.value) return 0
  return validatedData.value.data.filter(row => row.has_errors).length
})

// Calculate valid row count dynamically
const validRowCount = computed(() => {
  if (!validatedData.value) return 0
  return validatedData.value.data.filter(row => !row.has_errors).length
})

const handlePaste = (event) => {
  // Detect paste event and automatically start validation
  setTimeout(() => {
    console.log('Pasted data detected:', pastedText.value.substring(0, 100))
    if (pastedText.value.trim()) {
      processPastedData()
    }
  }, 100)
}

const parseTabDelimitedData = (text) => {
  // Split by newlines
  const lines = text.trim().split(/\r?\n/)
  const rows = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue

    // Split by tabs (Excel copy is tab-delimited)
    const columns = line.split('\t')

    // Check if there are 6 columns
    if (columns.length === 6) {
      rows.push({
        row_number: rows.length + 1,
        po_number: columns[0].trim(),
        product_code: columns[1].trim(),
        customer_name: columns[2].trim(),
        po_quantity: columns[3].trim(),
        date_receive_po: columns[4].trim(),
        delivery_date: columns[5].trim(),
        errors: {},
        has_errors: false,
        showAutocomplete: false,
        productSuggestions: [],
        customerAutoFilled: false
      })
    } else if (columns.length > 0) {
      console.warn(`Row ${i + 1} has ${columns.length} columns (expected 6):`, columns)
    }
  }

  return rows
}

const processPastedData = async () => {
  if (!pastedText.value.trim()) {
    alert('Please paste data')
    return
  }

  isProcessing.value = true
  isLoading.value = true

  try {
    // Parse tab-delimited data
    const parsedRows = parseTabDelimitedData(pastedText.value)

    if (parsedRows.length === 0) {
      alert('No valid data found.\n\nPlease paste 6-column data (PO Number, Product Code, Customer, Quantity, PO Received Date, Delivery Date).')
      return
    }

    // Use backend validation API
    const response = await api.post('/sales/po/clipboard/validate', {
      data: parsedRows
    })

    validatedData.value = response.data
  } catch (error) {
    console.error('Failed to validate data:', error)
    alert(error.response?.data?.detail || 'Failed to validate data')
  } finally {
    isProcessing.value = false
    isLoading.value = false
  }
}

const handleCellEdit = (rowIndex, fieldName) => {
  // Use debounce to auto-revalidate after editing
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

  // 1. Required fields check
  const required_fields = ['po_number', 'product_code', 'customer_name', 'po_quantity', 'date_receive_po', 'delivery_date']
  for (const field of required_fields) {
    if (!row[field] || !row[field].toString().trim()) {
      errors[field] = `${field} is empty`
    }
  }

  // 2. Quantity validation
  if (row.po_quantity) {
    const quantity = parseInt(row.po_quantity)
    if (isNaN(quantity) || quantity <= 0) {
      errors.po_quantity = "Quantity must be a positive integer"
    } else {
      row.po_quantity_int = quantity
    }
  }

  // 3. Simple date validation
  const dateFields = ['date_receive_po', 'delivery_date']
  for (const field of dateFields) {
    if (row[field]) {
      const dateStr = row[field].toString().trim()
      const datePatterns = [
        /^\d{4}-\d{2}-\d{2}$/,  // YYYY-MM-DD
        /^\d{1,2}\/\d{1,2}\/\d{4}$/,  // MM/DD/YYYY or DD/MM/YYYY
        /^\d{4}\/\d{2}\/\d{2}$/  // YYYY/MM/DD
      ]

      const isValidFormat = datePatterns.some(pattern => pattern.test(dateStr))
      if (!isValidFormat) {
        errors[field] = "Invalid date format (YYYY-MM-DD, MM/DD/YYYY, etc.)"
      }
    }
  }

  // Update errors
  row.errors = errors
  row.has_errors = Object.keys(errors).length > 0
}

const handleImport = async () => {
  if (!validatedData.value || validRowCount.value === 0) {
    return
  }

  isImporting.value = true

  try {
    // Prepare only rows without errors for registration
    const dataToImport = validatedData.value.data.filter(row => !row.has_errors)

    console.log('Importing data:', dataToImport)

    const response = await api.post('/sales/po/csv/import', dataToImport)
    alert(response.data.message)
    emit('import-success')

    // If there are error rows, keep only the error rows
    if (errorRowCount.value > 0) {
      const errorRows = validatedData.value.data.filter(row => row.has_errors)
      validatedData.value.data = errorRows
      validatedData.value.total_rows = errorRows.length
      validatedData.value.error_rows = errorRows.length

      // Re-number the rows
      errorRows.forEach((row, index) => {
        row.row_number = index + 1
      })
    } else {
      // If no error rows, fully reset
      resetImport()
    }
  } catch (error) {
    console.error('Failed to import data:', error)
    console.error('Error details:', error.response?.data)
    alert(error.response?.data?.detail || 'Failed to bulk import data')
  } finally {
    isImporting.value = false
  }
}

const resetImport = () => {
  validatedData.value = null
  pastedText.value = ''
}

// Autocomplete for product code input
const handleProductCodeInput = async (rowIndex) => {
  const row = validatedData.value.data[rowIndex]
  const query = row.product_code.trim()

  if (query.length < 1) {
    row.productSuggestions = []
    return
  }

  try {
    const response = await api.get('/master/autocomplete/products', {
      params: { search: query }
    })

    // Create suggestion data with product code and customer name
    row.productSuggestions = response.data.map(item => ({
      product_id: item.id,
      product_code: item.code,
      customer_name: item.customer_name || ''
    }))
  } catch (error) {
    console.error('Failed to fetch product suggestions:', error)
    row.productSuggestions = []
  }

  // Re-validate while typing
  handleCellEdit(rowIndex, 'product_code')
}

// Show autocomplete
const showAutocomplete = (rowIndex) => {
  const row = validatedData.value.data[rowIndex]
  row.showAutocomplete = true
}

// Hide autocomplete
const hideAutocomplete = (rowIndex) => {
  setTimeout(() => {
    const row = validatedData.value.data[rowIndex]
    row.showAutocomplete = false
  }, 200)
}

// Select product
const selectProduct = async (rowIndex, product) => {
  const row = validatedData.value.data[rowIndex]
  row.product_code = product.product_code
  row.customer_name = product.customer_name
  row.customerAutoFilled = true
  row.showAutocomplete = false
  row.productSuggestions = []

  // Re-validate both product code and customer name
  handleCellEdit(rowIndex, 'product_code')
  handleCellEdit(rowIndex, 'customer_name')
}
</script>

<style scoped>
.clipboard-import-container {
  width: 100%;
}

.paste-area-wrapper {
  width: 100%;
}

.paste-hint {
  margin: 0 0 var(--spacing-md) 0;
  padding: var(--spacing-sm) var(--spacing-md);
  background: #e8f4fd;
  border-left: 3px solid var(--primary);
  border-radius: 4px;
  font-size: 0.9rem;
  color: #004578;
}

.table-preview {
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.paste-row {
  background: #f9fbfd;
}

.paste-textarea-embedded {
  width: 100%;
  min-height: 120px;
  padding: var(--spacing-md);
  border: none;
  border-top: 2px dashed var(--border);
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  resize: vertical;
  transition: all 0.3s ease;
  background: transparent;
  text-align: center;
}

.paste-textarea-embedded:focus {
  outline: none;
  background: #fafbfc;
  border-top-color: var(--primary);
}

.paste-textarea-embedded::placeholder {
  color: var(--text-secondary);
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 0.9rem;
  text-align: center;
}

.paste-actions {
  margin-top: var(--spacing-md);
  text-align: right;
}

.loading {
  text-align: center;
  padding: var(--spacing-xl);
}

.spinner {
  border: 3px solid var(--border);
  border-top: 3px solid var(--primary);
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
  background: var(--light-bg);
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
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.preview-table th {
  background: var(--light-bg);
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 2px solid var(--border);
  font-weight: 600;
  position: sticky;
  top: 0;
}

.preview-table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--border);
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
  border-color: var(--primary);
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

.autocomplete-cell {
  position: relative;
  width: 100%;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  transition: background 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.autocomplete-item:hover {
  background: #f5f5f5;
}

.suggestion-code {
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
}

.suggestion-customer {
  font-size: 0.85rem;
  color: var(--text-secondary);
  flex-shrink: 0;
}
</style>
