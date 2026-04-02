<template>
  <AppLayout>
    <h1 class="page-title">Material Import - Label Printer</h1>

    <div class="card label-form-card">
      <h2>In Nhãn Quản Lý Lot Nguyên Liệu</h2>

      <form @submit.prevent="handlePrint">
        <div class="label-form-grid">
          <!-- Tên NL -->
          <div class="label-form-group">
            <label class="form-label">Tên NL:</label>
            <div class="autocomplete-wrapper">
              <input
                v-model="form.materialName"
                class="form-input"
                type="text"
                autocomplete="off"
                required
                @input="onAutocomplete('materialName', form.materialName, DATABASE.materials)"
                @keydown="onKeydown($event, 'materialName')"
                @blur="hideDropdown('materialName')"
              />
              <ul v-if="dropdowns.materialName.show && dropdowns.materialName.items.length" class="suggestions active">
                <li
                  v-for="(item, i) in dropdowns.materialName.items"
                  :key="item"
                  :class="{ selected: i === dropdowns.materialName.index }"
                  @mousedown.prevent="selectItem('materialName', item)"
                >{{ item }}</li>
              </ul>
            </div>
          </div>

          <!-- Size NL -->
          <div class="label-form-group">
            <label class="form-label">Size NL:</label>
            <div class="autocomplete-wrapper">
              <input
                v-model="form.materialSize"
                class="form-input"
                type="text"
                autocomplete="off"
                required
                @input="onAutocomplete('materialSize', form.materialSize, DATABASE.sizes)"
                @keydown="onKeydown($event, 'materialSize')"
                @blur="hideDropdown('materialSize')"
              />
              <ul v-if="dropdowns.materialSize.show && dropdowns.materialSize.items.length" class="suggestions active">
                <li
                  v-for="(item, i) in dropdowns.materialSize.items"
                  :key="item"
                  :class="{ selected: i === dropdowns.materialSize.index }"
                  @mousedown.prevent="selectItem('materialSize', item)"
                >{{ item }}</li>
              </ul>
            </div>
          </div>

          <!-- Nhà C.Cấp -->
          <div class="label-form-group">
            <label class="form-label">Nhà C.Cấp:</label>
            <div class="autocomplete-wrapper">
              <input
                v-model="form.supplier"
                class="form-input"
                type="text"
                autocomplete="off"
                required
                @input="onAutocomplete('supplier', form.supplier, DATABASE.suppliers)"
                @keydown="onKeydown($event, 'supplier')"
                @blur="hideDropdown('supplier')"
              />
              <ul v-if="dropdowns.supplier.show && dropdowns.supplier.items.length" class="suggestions active">
                <li
                  v-for="(item, i) in dropdowns.supplier.items"
                  :key="item"
                  :class="{ selected: i === dropdowns.supplier.index }"
                  @mousedown.prevent="selectItem('supplier', item)"
                >{{ item }}</li>
              </ul>
            </div>
          </div>

          <!-- Số lot (auto) -->
          <div class="label-form-group">
            <label class="form-label">Số lot:</label>
            <input :value="lotCode" class="form-input" type="text" readonly />
          </div>

          <!-- Ngày nhập -->
          <div class="label-form-group">
            <label class="form-label">Ngày nhập:</label>
            <input v-model="form.entryDate" class="form-input" type="text" required placeholder="DD/MM/YYYY" />
          </div>

          <!-- Đóng dấu -->
          <div class="label-form-group">
            <label class="form-label">Đóng dấu:</label>
            <input v-model="form.certification" class="form-input" type="text" readonly />
          </div>

          <!-- Số lượng -->
          <div class="label-form-group">
            <label class="form-label">Số lượng (kg):</label>
            <input
              v-model="form.weight"
              class="form-input"
              type="number"
              min="1"
              max="999999"
              required
              placeholder="Nhập số lượng..."
              @input="onWeightInput"
            />
          </div>
        </div>

        <div style="margin-top: var(--spacing-lg);">
          <button type="submit" class="btn btn-primary" style="padding: 12px 40px; font-size: 16px;">In nhãn</button>
        </div>
      </form>
    </div>

    <!-- Print Area (hidden on screen, visible on print) -->
    <div id="materialLabelPrintArea" class="print-area">
      <div class="label-container">
        <div class="label-header-title">PHIẾU QUẢN LÝ LOT NGUYÊN LIỆU</div>
        <div class="label-content">
          <table class="label-table">
            <tbody>
              <tr>
                <td class="label-header">Tên NL</td>
                <td class="label-value">{{ form.materialName }}</td>
              </tr>
              <tr>
                <td class="label-header">Size NL</td>
                <td class="label-value">{{ form.materialSize }}</td>
              </tr>
              <tr>
                <td class="label-header">Nhà C.Cấp</td>
                <td class="label-value">{{ form.supplier }}</td>
              </tr>
              <tr>
                <td class="label-header">Số lot</td>
                <td class="label-value">{{ lotCode }}</td>
              </tr>
              <tr>
                <td class="label-header">Ngày nhập</td>
                <td class="label-value">{{ form.entryDate }}</td>
              </tr>
              <tr>
                <td class="label-header">Đóng dấu</td>
                <td class="label-value">{{ form.certification }}</td>
              </tr>
              <tr>
                <td class="label-header">Số lượng</td>
                <td class="label-value">{{ form.weight }} kg ( {{ form.entryDate.replace(/\//g, '-') }} )</td>
              </tr>
            </tbody>
          </table>
          <div class="qr-cell" ref="qrCellRef"></div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import QRCode from 'qrcodejs2-fix'

// Sample database (後ほどDB連携に置き換え)
const DATABASE = {
  materials: [
    'SPCC-SD', 'SPCC-SB', 'SPCC-1D', 'SECC', 'SECC-O', 'SGCC',
    'SUS304', 'SUS304-2B', 'SUS316', 'SUS430',
    'A1050', 'A1100', 'A5052', 'A6061',
    'C1100', 'C2801', 'SPHC', 'SPHD', 'SPHE', 'SS400'
  ],
  sizes: [
    '0.5*100*C', '0.6*100*C', '0.8*100*C', '1.0*100*C', '1.0*150*C',
    '1.2*100*C', '1.2*150*C', '1.5*100*C', '1.5*150*C', '1.6*100*C',
    '1.6*150*C', '2.0*100*C', '2.0*150*C', '2.3*100*C', '2.3*150*C',
    '3.0*100*C', '3.0*150*C', '0.5*1219*C', '0.6*1219*C', '0.8*1219*C',
    '1.0*1219*C', '1.2*1219*C', '1.5*1219*C', '1.6*1219*C', '2.0*1219*C'
  ],
  suppliers: [
    'JFE', 'NIPPON STEEL', 'POSCO', 'HYUNDAI STEEL', 'CSC',
    'CHINA STEEL', 'BAOSTEEL', 'TATA STEEL', 'SSAB', 'THYSSENKRUPP',
    'ARCELOR MITTAL', 'KOBE STEEL', 'NISSHIN STEEL', 'SUMITOMO METAL', 'KOBELCO'
  ]
}

// Form
const today = new Date()
const dd = String(today.getDate()).padStart(2, '0')
const mm = String(today.getMonth() + 1).padStart(2, '0')
const yyyy = today.getFullYear()

const form = reactive({
  materialName: '',
  materialSize: '',
  supplier: '',
  entryDate: `${dd}/${mm}/${yyyy}`,
  certification: 'OK. ĐẠT RoHS',
  weight: ''
})

// Lot code (auto-generated)
const lotCode = computed(() => {
  const material = form.materialName.trim()
  const supplier = form.supplier.trim()
  const parts = form.entryDate.split('/')
  if (material && supplier && parts.length === 3) {
    const dateStr = parts[0] + parts[1] + parts[2].slice(-2)
    return `${material} ${dateStr} ${supplier}`
  }
  return ''
})

// Autocomplete state
const dropdowns = reactive({
  materialName: { show: false, items: [], index: -1 },
  materialSize: { show: false, items: [], index: -1 },
  supplier: { show: false, items: [], index: -1 },
})

let debounceTimers = {}

function onAutocomplete(field, value, dataSource) {
  clearTimeout(debounceTimers[field])
  const v = value.trim()
  if (!v) {
    dropdowns[field].show = false
    dropdowns[field].items = []
    return
  }
  debounceTimers[field] = setTimeout(() => {
    const matches = dataSource.filter(d => d.toLowerCase().includes(v.toLowerCase()))
    if (matches.length === 1) {
      form[field] = matches[0]
      dropdowns[field].show = false
      dropdowns[field].items = []
    } else if (matches.length > 0) {
      dropdowns[field].items = matches
      dropdowns[field].index = -1
      dropdowns[field].show = true
    } else {
      dropdowns[field].show = false
      dropdowns[field].items = []
    }
  }, 200)
}

function onKeydown(e, field) {
  const dd = dropdowns[field]
  if (!dd.show || !dd.items.length) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    dd.index = Math.min(dd.index + 1, dd.items.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    dd.index = Math.max(dd.index - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (dd.index >= 0 && dd.items[dd.index]) {
      selectItem(field, dd.items[dd.index])
    }
  } else if (e.key === 'Escape') {
    dd.show = false
  }
}

function selectItem(field, value) {
  form[field] = value
  dropdowns[field].show = false
  dropdowns[field].items = []
}

function hideDropdown(field) {
  setTimeout(() => {
    dropdowns[field].show = false
  }, 200)
}

function onWeightInput() {
  let v = String(form.weight).replace(/\D/g, '')
  if (v.length > 6) v = v.slice(0, 6)
  form.weight = v ? Number(v) : ''
}

// QR Code
const qrCellRef = ref(null)

function generateQRCode() {
  if (!qrCellRef.value) return
  qrCellRef.value.innerHTML = ''

  const qrData = [
    form.materialName,
    form.materialSize,
    form.supplier,
    lotCode.value,
    form.entryDate,
    form.weight + ' kg'
  ].join('\n')

  try {
    new QRCode(qrCellRef.value, {
      text: qrData,
      width: 200,
      height: 200,
      colorDark: '#000000',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.M
    })
  } catch (error) {
    console.error('QR Code generation error:', error)
  }
}

// Validation & Print
function validateForm() {
  if (!form.materialName.trim()) { alert('Vui lòng nhập Tên NL'); return false }
  if (!form.materialSize.trim()) { alert('Vui lòng nhập Size NL'); return false }
  if (!form.supplier.trim()) { alert('Vui lòng nhập Nhà C.Cấp'); return false }
  if (!form.entryDate.trim()) { alert('Vui lòng nhập Ngày nhập'); return false }

  const dateRegex = /^\d{2}\/\d{2}\/\d{4}$/
  if (!dateRegex.test(form.entryDate)) {
    alert('Vui lòng nhập ngày đúng định dạng DD/MM/YYYY')
    return false
  }

  const weight = parseInt(form.weight)
  if (isNaN(weight) || weight < 1 || weight > 999999) {
    alert('Trọng lượng phải là số từ 1 đến 999999')
    return false
  }

  return true
}

async function handlePrint() {
  if (!validateForm()) return
  await nextTick()
  generateQRCode()
  await nextTick()
  window.print()
}
</script>

<style scoped>
.label-form-card {
  max-width: 650px;
}

.label-form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.label-form-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label-form-group .form-label {
  width: 120px;
  min-width: 120px;
  margin-bottom: 0;
  font-weight: 600;
  color: #34495e;
}

.label-form-group .form-input {
  flex: 1;
  max-width: 400px;
}

.label-form-group .form-input[readonly] {
  background-color: #ecf0f1;
  cursor: not-allowed;
}

/* Autocomplete */
.autocomplete-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.autocomplete-wrapper .form-input {
  max-width: 100%;
  width: 100%;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 5px 5px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  list-style: none;
  margin: 0;
  padding: 0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.suggestions li {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.suggestions li:last-child {
  border-bottom: none;
}

.suggestions li:hover,
.suggestions li.selected {
  background-color: #3498db;
  color: white;
}

/* Print area hidden on screen */
.print-area {
  display: none;
}

/* Label Container - A7 (74mm x 105mm) */
.label-container {
  width: 74mm;
  height: 105mm;
  background: white;
  padding: 2mm;
  box-sizing: border-box;
  border: 1px solid #000;
}

.label-header-title {
  font-size: 10pt;
  font-weight: bold;
  text-align: center;
  padding: 1.5mm;
  background-color: #f0f0f0;
}

.label-content {
  display: flex;
  flex-direction: column;
  height: calc(100% - 8mm);
}

.label-table {
  flex: 1;
  border-collapse: collapse;
  font-size: 9pt;
  width: 100%;
}

.label-table td {
  border: 1px solid #000;
  padding: 0.5mm 1mm;
  text-align: left;
}

.label-header {
  width: 18mm;
  font-weight: normal;
  white-space: nowrap;
  font-size: 8pt;
}

.label-value {
  font-weight: bold;
  text-align: center !important;
  font-size: 9pt;
}

.qr-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #000;
  padding: 1mm;
  flex: 1;
}

.qr-cell :deep(canvas),
.qr-cell :deep(img) {
  width: 33mm !important;
  height: 33mm !important;
  max-width: 33mm;
  max-height: 33mm;
}
</style>

<style>
/* Print styles (global, not scoped) */
@media print {
  @page {
    size: 74mm 105mm;
    margin: 0;
  }

  body {
    margin: 0 !important;
    padding: 0 !important;
    background: white !important;
  }

  /* Hide everything except print area */
  .app-sidebar,
  .app-header,
  .app-main > *:not(#materialLabelPrintArea),
  .page-title,
  .label-form-card {
    display: none !important;
  }

  #materialLabelPrintArea {
    display: block !important;
    position: static;
    background: white;
    padding: 0;
  }

  #materialLabelPrintArea .label-container {
    width: 74mm;
    height: 105mm;
    margin: 0;
    padding: 2mm;
    page-break-after: avoid;
    page-break-inside: avoid;
  }
}
</style>
