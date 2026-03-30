<template>
  <AppLayout>
    <div class="purchase-container">
      <!-- Print/Action Buttons -->
      <div class="action-buttons">
        <button type="button" class="btn btn-primary" @click="handlePrint">Print</button>
      </div>

      <!-- Header -->
      <div class="po-header">
        <h1>PURCHASE ORDER</h1>
        <div class="doc-info">
          <span>M-02/QT02-KD</span>
          <span>Lần sửa đổi: 05(23/03/2016)</span>
        </div>
      </div>

      <!-- Recipient Information -->
      <div class="info-section">
        <div class="info-row">
          <label>To :</label>
          <input type="text" v-model="header.to" class="wide-input">
        </div>
        <div class="info-row">
          <label>Attn :</label>
          <input type="text" v-model="header.attn_to" class="wide-input">
        </div>
        <div class="info-row">
          <label>Tel :</label>
          <input type="text" v-model="header.tel" class="wide-input">
        </div>
      </div>

      <!-- Sender Information -->
      <div class="info-section">
        <div class="info-row">
          <label>From :</label>
          <span class="static-text">HIROTA PRECISION VN CO., LTD</span>
        </div>
        <div class="info-row">
          <label>Attn:</label>
          <input type="text" v-model="header.attn_from">
        </div>
        <div class="info-row">
          <label>H/P:</label>
          <input type="text" v-model="header.hp">
        </div>
        <div class="info-row">
          <label>P/O no:</label>
          <input type="text" v-model="header.po_no">
        </div>
        <div class="info-row">
          <label>Date :</label>
          <input type="text" v-model="header.date" placeholder="dd/mm/yyyy" maxlength="10"
            class="date-input" @keydown="handleDateKeydown" @click="handleDateClick" @focus="handleDateFocus">
        </div>
        <div class="info-row">
          <label>Currency :</label>
          <select v-model="header.currency">
            <option value="VND">VND</option>
            <option value="USD">USD</option>
            <option value="JPY">JPY</option>
          </select>
        </div>
      </div>

      <!-- Items Table -->
      <table class="items-table" ref="itemsTableRef">
        <thead>
          <tr>
            <th class="col-no">NO</th>
            <th class="col-material">Material</th>
            <th class="col-description" colspan="3">DESCRIPTION</th>
            <th class="col-quantity">QUANTITY<br>(kg/pcs)</th>
            <th class="col-price">UNIT PRICE<br>({{ header.currency }}/KG)</th>
            <th class="col-price-sheet">UNIT PRICE<br>({{ header.currency }}/Tấm)</th>
            <th class="col-amount">TOTAL<br>AMOUNT</th>
            <th class="col-delivery">DELIVERY<br>DATE</th>
            <th class="col-remark">REMARK</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="item.id" class="item-row">
            <td class="col-no">
              {{ index + 1 }}
              <button v-if="index === items.length - 1" type="button" class="add-row-btn no-print" @click="addRow">+</button>
            </td>
            <td>
              <textarea v-model="item.material" class="material-input" rows="1"
                @input="onItemChange(index); autoResize($event)"
                @keydown="handleTableKeydown($event, index, 'material')"></textarea>
            </td>
            <td class="desc-cell">
              <textarea v-model="item.desc1" class="desc1-input" rows="1"
                @input="onItemChange(index); autoResize($event)"
                @keydown="handleTableKeydown($event, index, 'desc1')"></textarea>
              <button type="button" class="tol-btn no-print" :class="{ 'has-tol': item.tol1Plus || item.tol1Minus }"
                @click.stop="openTolerance(index, 1, $event)">±</button>
              <span class="tol-display">{{ formatTolerance(item.tol1Plus, item.tol1Minus) }}</span>
            </td>
            <td class="desc-cell">
              <input type="text" v-model="item.desc2"
                @input="onItemChange(index)"
                @keydown="handleTableKeydown($event, index, 'desc2')">
              <button type="button" class="tol-btn no-print" :class="{ 'has-tol': item.tol2Plus || item.tol2Minus }"
                @click.stop="openTolerance(index, 2, $event)">±</button>
              <span class="tol-display">{{ formatTolerance(item.tol2Plus, item.tol2Minus) }}</span>
            </td>
            <td class="desc-cell">
              <input type="text" v-model="item.desc3"
                @input="onItemChange(index)"
                @keydown="handleTableKeydown($event, index, 'desc3')">
              <button type="button" class="tol-btn no-print" :class="{ 'has-tol': item.tol3Plus || item.tol3Minus }"
                @click.stop="openTolerance(index, 3, $event)">±</button>
              <span class="tol-display">{{ formatTolerance(item.tol3Plus, item.tol3Minus) }}</span>
            </td>
            <td class="quantity-cell">
              <input type="text" v-model="item.quantityDisplay" class="quantity-input" inputmode="decimal"
                @focus="onQuantityFocus(index)" @blur="onQuantityBlur(index)"
                @keydown="handleTableKeydown($event, index, 'quantity')">
              <span class="quantity-unit">{{ getQuantityUnit(item) }}</span>
            </td>
            <td>
              <input type="text" v-model="item.priceDisplay" class="price-input" inputmode="decimal"
                @focus="onPriceFocus(index)" @blur="onPriceBlur(index)"
                @keydown="handleTableKeydown($event, index, 'price')">
            </td>
            <td class="price-sheet-cell">{{ getPricePerSheet(item) }}</td>
            <td class="amount-cell">{{ formatNumber(calculateRowAmount(item)) }}</td>
            <td>
              <input type="text" v-model="item.delivery_date" class="date-input"
                placeholder="dd/mm/yyyy" maxlength="10"
                :class="{ 'date-default': item.isDefaultDate }"
                @keydown="handleDateKeydown($event); markDateChanged(item)"
                @click="handleDateClick" @focus="handleDateFocus"
                @keydown.enter="handleTableKeydown($event, index, 'delivery_date')">
            </td>
            <td>
              <textarea v-model="item.remark" class="remark-input" rows="1"
                @input="autoResize($event)"
                @keydown="handleTableKeydown($event, index, 'remark')"></textarea>
              <button type="button" class="delete-btn no-print" @click="deleteRow(index)">×</button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="total-row">
            <td colspan="8" class="total-label">Grand Total</td>
            <td class="grand-total">{{ formatNumber(grandTotal) }}</td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>

      <!-- Condition Section -->
      <div class="condition-section">
        <h3><u>CONDITION:</u></h3>
        <p>Commodity: good, right feature, new and good quality, not scratch on the surface. The material must be reached RoHS standard.</p>
        <p>Attached document: Certificate of Origin, Certificate of Quality, RoHS certificate.</p>
        <p>Packing: Good condition</p>
        <p>Tolerance: ± 10% for weight</p>
        <p>Delivery time: Before 4 p.m.</p>
        <p>Delivery place: AT HIROTA PRECISION VN FACTORY</p>
      </div>

      <!-- Signature Section -->
      <div class="signature-section">
        <table class="signature-table">
          <thead>
            <tr>
              <th>Confirmed</th>
              <th>Purchasing</th>
              <th>Checked by</th>
              <th></th>
              <th>Approved by</th>
              <th>Approved by</th>
            </tr>
          </thead>
          <tbody>
            <tr class="signature-space">
              <td></td><td></td><td></td><td></td><td></td><td></td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="date-row">
              <td v-for="n in 6" :key="n">Date: <input type="text" class="sign-date"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Footer -->
      <div class="po-footer">
        <span class="footer-left">QUY TRÌNH MUA HÀNG</span>
        <span class="footer-right">Thời gian lưu trữ: 15 năm</span>
      </div>

      <!-- Tolerance Popover -->
      <div v-if="tolPopover.show" class="tol-popover show" :style="{ left: tolPopover.x + 'px', top: tolPopover.y + 'px' }"
        @click.stop>
        <div class="tol-row">
          <label>+</label>
          <input type="text" v-model="tolPopover.plus" ref="tolPlusRef" @keydown.enter="closeTolerance" @keydown.escape="closeTolerance">
        </div>
        <div class="tol-row">
          <label>−</label>
          <input type="text" v-model="tolPopover.minus" @keydown.enter="closeTolerance" @keydown.escape="closeTolerance"
            @keydown.tab.prevent="closeTolerance">
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'

// --- Density Table ---
const DENSITY_TABLE = {
  'SUS304': 7.93, 'SUS316': 7.98, 'SUS430': 7.70,
  'SS400': 7.85, 'S45C': 7.85, 'S50C': 7.85,
  'SK3': 7.85, 'SKD11': 7.85, 'SKD61': 7.85, 'SCM440': 7.85,
  'A5052': 2.68, 'A5056': 2.64, 'A6061': 2.70, 'A6063': 2.70, 'A7075': 2.80, 'A2017': 2.79,
  'C1100': 8.94, 'C2801': 8.47, 'C3604': 8.50,
  'SPCC': 7.85, 'SECC': 7.85, 'SPHC': 7.85,
}

// --- Date helpers ---
function formatDateDMY(date) {
  const d = String(date.getDate()).padStart(2, '0')
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const y = date.getFullYear()
  return `${d}/${m}/${y}`
}

function getTomorrow() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return formatDateDMY(d)
}

// --- Header ---
const header = reactive({
  to: '',
  attn_to: '',
  tel: '',
  attn_from: 'Ms.Nga',
  hp: '0909133392',
  po_no: '',
  date: formatDateDMY(new Date()),
  currency: 'VND',
})

// --- Items ---
let nextId = 1
function createItem() {
  return {
    id: nextId++,
    material: '',
    desc1: '',
    desc2: '',
    desc3: '',
    quantity: 0,
    quantityDisplay: '',
    unitPrice: 0,
    priceDisplay: '',
    delivery_date: getTomorrow(),
    isDefaultDate: true,
    remark: '',
    tol1Plus: '', tol1Minus: '',
    tol2Plus: '', tol2Minus: '',
    tol3Plus: '', tol3Minus: '',
  }
}

const items = reactive([createItem()])
const itemsTableRef = ref(null)

// --- Number formatting ---
function formatWithComma(num) {
  const n = parseFloat(String(num).replace(/,/g, ''))
  if (isNaN(n)) return ''
  const parts = n.toString().split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return parts.join('.')
}

function formatNumber(num) {
  return Math.round(num).toLocaleString('en-US')
}

// --- Quantity/Price focus/blur ---
function onQuantityFocus(index) {
  const item = items[index]
  item.quantityDisplay = item.quantityDisplay.replace(/,/g, '')
}

function onQuantityBlur(index) {
  const item = items[index]
  const val = item.quantityDisplay.replace(/,/g, '')
  item.quantity = parseFloat(val) || 0
  if (val !== '' && !isNaN(parseFloat(val))) {
    item.quantityDisplay = formatWithComma(val)
  }
}

function onPriceFocus(index) {
  const item = items[index]
  item.priceDisplay = item.priceDisplay.replace(/,/g, '')
}

function onPriceBlur(index) {
  const item = items[index]
  const val = item.priceDisplay.replace(/,/g, '')
  item.unitPrice = parseFloat(val) || 0
  if (val !== '' && !isNaN(parseFloat(val))) {
    item.priceDisplay = formatWithComma(val)
  }
}

// --- Calculations ---
function getQuantityUnit(item) {
  const d3 = item.desc3.trim().toUpperCase()
  if (d3 === '') return ''
  if (d3 === 'C') return 'kg'
  if (!isNaN(parseFloat(d3))) return 'sheet'
  return ''
}

function calculateRowAmount(item) {
  const d3 = item.desc3.trim().toUpperCase()
  const qty = parseFloat(String(item.quantityDisplay).replace(/,/g, '')) || 0
  const price = parseFloat(String(item.priceDisplay).replace(/,/g, '')) || 0

  if (d3 === 'C' || d3 === '') {
    return qty * price
  }

  const d3Num = parseFloat(d3)
  if (!isNaN(d3Num)) {
    const d1 = parseFloat(item.desc1) || 0
    const d2 = parseFloat(item.desc2) || 0
    const material = item.material.trim().toUpperCase()
    const density = DENSITY_TABLE[material]
    if (d1 && d2 && d3Num && density && price) {
      const kgPerSheet = (d1 * d2 * d3Num * density) / 1000000
      return kgPerSheet * qty * price
    }
  }
  return 0
}

function getPricePerSheet(item) {
  const d3 = item.desc3.trim().toUpperCase()
  if (d3 === 'C' || d3 === '') return ''
  const d3Num = parseFloat(d3)
  if (isNaN(d3Num)) return ''

  const d1 = parseFloat(item.desc1) || 0
  const d2 = parseFloat(item.desc2) || 0
  const price = parseFloat(String(item.priceDisplay).replace(/,/g, '')) || 0
  const material = item.material.trim().toUpperCase()
  const density = DENSITY_TABLE[material]
  if (d1 && d2 && d3Num && density && price) {
    const kgPerSheet = (d1 * d2 * d3Num * density) / 1000000
    return formatNumber(kgPerSheet * price)
  }
  return ''
}

const grandTotal = computed(() => {
  return items.reduce((sum, item) => sum + calculateRowAmount(item), 0)
})

function onItemChange(_index) {
  // Reactivity handles recalculation automatically
}

// --- Row management ---
function addRow() {
  items.push(createItem())
  nextTick(() => {
    const tbody = itemsTableRef.value?.querySelector('tbody')
    if (tbody) {
      const lastRow = tbody.querySelector('tr:last-child')
      lastRow?.querySelector('.material-input')?.focus()
    }
  })
}

function deleteRow(index) {
  if (items.length <= 1) {
    alert('At least one row is required.')
    return
  }
  items.splice(index, 1)
}

// --- Tolerance Popover ---
const tolPopover = reactive({ show: false, x: 0, y: 0, plus: '', minus: '', itemIndex: 0, descNum: 1 })
const tolPlusRef = ref(null)

function formatTolerance(plus, minus) {
  let text = ''
  if (plus) text += '+' + plus
  if (minus) text += (text ? ' ' : '') + '−' + minus
  return text
}

function openTolerance(itemIndex, descNum, event) {
  const rect = event.target.getBoundingClientRect()
  const item = items[itemIndex]
  tolPopover.itemIndex = itemIndex
  tolPopover.descNum = descNum
  tolPopover.plus = item[`tol${descNum}Plus`]
  tolPopover.minus = item[`tol${descNum}Minus`]
  tolPopover.x = rect.left
  tolPopover.y = rect.bottom + 2
  tolPopover.show = true
  nextTick(() => tolPlusRef.value?.focus())
}

function closeTolerance() {
  const item = items[tolPopover.itemIndex]
  const n = tolPopover.descNum
  item[`tol${n}Plus`] = tolPopover.plus
  item[`tol${n}Minus`] = tolPopover.minus
  tolPopover.show = false
}

function onDocumentClick() {
  if (tolPopover.show) closeTolerance()
}

onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))

// --- Auto resize textarea ---
function autoResize(event) {
  const el = event.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// --- Date input section-based editing ---
function getDateSection(pos) {
  if (pos <= 2) return 0
  if (pos <= 5) return 1
  return 2
}

function selectDateSection(input, sec) {
  const ranges = [[0, 2], [3, 5], [6, 10]]
  const r = ranges[sec] || ranges[0]
  setTimeout(() => input.setSelectionRange(r[0], r[1]), 0)
}

function handleDateClick(e) {
  const input = e.target
  if (input.value.length === 10) {
    const sec = getDateSection(input.selectionStart)
    input._dateSec = sec
    input._dateClean = true
    selectDateSection(input, sec)
  }
}

function handleDateFocus(e) {
  const input = e.target
  if (input.value.length === 10) {
    input._dateSec = 0
    input._dateClean = true
    selectDateSection(input, 0)
  }
}

function handleDateKeydown(e) {
  const t = e.target
  if (!t.classList.contains('date-input') && !t.classList.contains('sign-date')) return

  const val = t.value
  const sec = (t._dateSec != null) ? t._dateSec : getDateSection(t.selectionStart)
  const parts = val.split('/')

  if (e.key === 'ArrowLeft') {
    if (sec > 0) { e.preventDefault(); t._dateSec = sec - 1; t._dateClean = true; selectDateSection(t, sec - 1) }
    return
  }
  if (e.key === 'ArrowRight') {
    if (sec < 2) { e.preventDefault(); t._dateSec = sec + 1; t._dateClean = true; selectDateSection(t, sec + 1) }
    return
  }
  if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    e.preventDefault()
    if (parts.length !== 3) return
    let n = parseInt(parts[sec], 10) || 0
    n += (e.key === 'ArrowUp') ? 1 : -1
    const maxes = [31, 12, 9999]
    const mins = [1, 1, 2000]
    if (n > maxes[sec]) n = mins[sec]
    if (n < mins[sec]) n = maxes[sec]
    const pads = [2, 2, 4]
    parts[sec] = String(n).padStart(pads[sec], '0')
    t.value = parts.join('/')
    // Update v-model manually
    t.dispatchEvent(new Event('input'))
    t._dateClean = true
    selectDateSection(t, sec)
    return
  }
  if (e.key === 'Backspace') {
    e.preventDefault()
    if (parts.length !== 3) return
    const pads = [2, 2, 4]
    parts[sec] = '0'.repeat(pads[sec])
    t.value = parts.join('/')
    t.dispatchEvent(new Event('input'))
    t._dateClean = true
    selectDateSection(t, sec)
    return
  }
  if (e.key === 'Tab' || e.key === 'Enter') return

  if (/^\d$/.test(e.key)) {
    e.preventDefault()
    if (parts.length !== 3) {
      t.value = '00/00/0000'
      t.dispatchEvent(new Event('input'))
      parts[0] = '00'; parts[1] = '00'; parts[2] = '0000'
      t._dateSec = 0
      t._dateClean = true
    }
    const pads = [2, 2, 4]
    let cur
    if (t._dateClean) {
      cur = ''
      t._dateClean = false
    } else {
      cur = parts[sec].replace(/\D/g, '')
    }
    cur += e.key
    if (cur.length >= pads[sec]) {
      parts[sec] = cur.slice(-pads[sec])
      t.value = parts.join('/')
      t.dispatchEvent(new Event('input'))
      if (sec < 2) {
        t._dateSec = sec + 1
        t._dateClean = true
        selectDateSection(t, sec + 1)
      } else {
        selectDateSection(t, sec)
      }
    } else {
      parts[sec] = cur.padStart(pads[sec], '0')
      t.value = parts.join('/')
      t.dispatchEvent(new Event('input'))
      selectDateSection(t, sec)
    }
    return
  }

  if (e.key !== 'Tab') e.preventDefault()
}

function markDateChanged(item) {
  if (item.isDefaultDate) item.isDefaultDate = false
}

// --- Enter key navigation ---
function handleTableKeydown(e, rowIndex, field) {
  if (e.key !== 'Enter') return
  if (e.target.matches('textarea') && e.shiftKey) return // Shift+Enter for newline in textarea

  e.preventDefault()

  if (field === 'remark') {
    addRow()
    return
  }

  // Move to next input in the row/table
  const table = itemsTableRef.value
  if (!table) return
  const allInputs = Array.from(table.querySelectorAll('input, textarea'))
  const idx = allInputs.indexOf(e.target)
  if (idx >= 0 && idx < allInputs.length - 1) {
    allInputs[idx + 1].focus()
  }
}

// --- Print ---
function handlePrint() {
  window.print()
}
</script>

<style scoped>
/* Base */
.purchase-container {
  max-width: 210mm;
  margin: 0 auto;
  padding: 15mm;
  background-color: white;
  font-family: Arial, sans-serif;
  font-size: 12px;
  line-height: 1.4;
  position: relative;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: flex-end;
}

/* Header */
.po-header {
  text-align: center;
  margin-bottom: 15px;
  position: relative;
}

.po-header h1 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.doc-info {
  position: absolute;
  right: 0;
  top: 0;
  text-align: right;
  font-size: 10px;
}

.doc-info span {
  display: block;
}

/* Info Sections */
.info-section {
  margin-bottom: 10px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 3px;
}

.info-row label {
  width: 70px;
  font-weight: normal;
}

.info-row input,
.info-row select {
  padding: 3px 5px;
  border: 1px solid #ccc;
  font-size: 12px;
}

.info-row .wide-input {
  width: 300px;
}

.info-row input:not(.wide-input):not(.date-input) {
  width: 200px;
}

.info-row .date-input {
  width: 200px;
}

.info-row select {
  width: 100px;
}

.static-text {
  font-weight: bold;
}

/* Items Table */
.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.items-table th,
.items-table td {
  border: 1px solid #000;
  padding: 2px 1px;
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
  overflow: visible;
}

.items-table th {
  background-color: #f0f0f0;
  font-weight: bold;
  font-size: 10px;
  white-space: normal;
  word-break: keep-all;
}

.items-table td {
  min-height: 30px;
}

.items-table td:last-child {
  white-space: normal;
  position: relative;
}

/* Column Min Widths */
.col-no { min-width: 26px; width: 26px; position: relative; }
.col-material { min-width: 62px; }
.col-description { min-width: 40px; }
.col-quantity { min-width: 70px; }
.col-price { min-width: 65px; }
.col-price-sheet { min-width: 65px; }
.col-amount { min-width: 65px; }
.col-delivery { min-width: 72px; }
.col-remark { min-width: 80px; }

/* Textareas */
.material-input,
.desc1-input {
  resize: none;
  overflow: hidden;
  min-height: 20px;
  max-height: 80px;
  font-family: Arial, sans-serif;
  font-size: 11px;
  border: none;
  padding: 2px 1px;
  text-align: center;
  background: transparent;
  width: 100%;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.material-input:focus,
.desc1-input:focus {
  outline: 2px solid #4CAF50;
  background: #fff;
}

/* Input Styles in Table */
.items-table input {
  width: 100%;
  border: none;
  padding: 2px 1px;
  font-size: 11px;
  text-align: center;
  background: transparent;
  overflow: visible;
  text-overflow: clip;
}

.items-table input:focus {
  outline: 2px solid #4CAF50;
  background: #fff;
}

.quantity-input,
.price-input {
  text-align: right !important;
}

.items-table .date-input {
  font-size: 10px;
}

.quantity-cell .quantity-input {
  width: calc(100% - 30px) !important;
  text-align: right !important;
}

.date-default {
  background-color: #e8f5e9 !important;
}

.quantity-unit {
  font-size: 8px;
  color: #888;
  display: inline-block;
  width: 26px;
  text-align: left;
  padding-left: 2px;
}

.amount-cell {
  text-align: right;
  padding-right: 8px !important;
  font-weight: bold;
  white-space: nowrap;
}

.price-sheet-cell {
  text-align: right;
  padding-right: 8px !important;
  color: #333;
  white-space: nowrap;
}

/* Tolerance */
.desc-cell {
  position: relative;
}

.tol-btn {
  position: absolute;
  top: 1px;
  right: 1px;
  width: 14px;
  height: 14px;
  font-size: 9px;
  line-height: 1;
  background: #e0e0e0;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  color: #666;
  padding: 0;
  display: none;
  z-index: 1;
}

.desc-cell:hover .tol-btn,
.tol-btn.has-tol {
  display: block;
}

.tol-popover {
  position: fixed;
  background: #fff;
  border: 1px solid #999;
  border-radius: 4px;
  padding: 6px 8px;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  white-space: nowrap;
}

.tol-popover label {
  font-size: 10px;
  color: #333;
  margin-right: 2px;
}

.tol-popover input {
  width: 55px;
  font-size: 10px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  border-radius: 2px;
  text-align: right;
}

.tol-popover .tol-row {
  margin-bottom: 3px;
}

.tol-popover .tol-row:last-child {
  margin-bottom: 0;
}

.tol-display {
  display: block;
  font-size: 8px;
  color: #666;
  line-height: 1.1;
  text-align: center;
}

/* Total Row */
.total-row td {
  font-weight: bold;
}

.total-label {
  text-align: right;
  padding-right: 10px !important;
}

.grand-total {
  text-align: right;
  padding-right: 8px !important;
  font-size: 14px;
}

/* Add/Delete buttons */
.add-row-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
}

.add-row-btn:hover {
  background: #388E3C;
}

.delete-btn {
  position: absolute;
  right: 2px;
  top: 50%;
  transform: translateY(-50%);
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  cursor: pointer;
  line-height: 1;
}

.delete-btn:hover {
  background: #cc0000;
}

/* Remark */
.remark-input {
  width: calc(100% - 20px) !important;
  resize: none;
  overflow: hidden;
  min-height: 20px;
  max-height: 80px;
  font-family: Arial, sans-serif;
  font-size: 11px;
  border: none;
  padding: 3px;
  text-align: center;
  background: transparent;
  vertical-align: middle;
  display: block;
}

.remark-input:focus {
  outline: 2px solid #4CAF50;
  background: #fff;
}

/* Condition */
.condition-section {
  margin-bottom: 20px;
  font-size: 11px;
}

.condition-section h3 {
  font-size: 12px;
  margin-bottom: 5px;
}

.condition-section p {
  margin-bottom: 2px;
}

/* Signature */
.signature-section {
  margin-top: 30px;
  margin-bottom: 20px;
}

.signature-table {
  width: 100%;
  border-collapse: collapse;
}

.signature-table th,
.signature-table td {
  border: 1px solid #000;
  padding: 5px;
  text-align: center;
  width: 16.66%;
}

.signature-table th {
  font-weight: normal;
  font-style: italic;
  height: 25px;
}

.signature-space td {
  height: 80px;
  vertical-align: bottom;
}

.date-row td {
  text-align: left;
  font-size: 10px;
  height: 25px;
}

.sign-date {
  border: none;
  border-bottom: 1px solid #ccc;
  width: 70px;
  font-size: 10px;
  background: transparent;
}

/* Footer */
.po-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 10px;
}

/* Print */
@media print {
  .purchase-container {
    max-width: 100%;
    margin: 0;
    padding: 10mm;
    box-shadow: none;
  }

  .no-print {
    display: none !important;
  }

  .delete-btn {
    display: none !important;
  }

  .tol-btn, .tol-popover {
    display: none !important;
  }

  .info-row input,
  .info-row select,
  .items-table input,
  .sign-date {
    border: none;
    background: transparent;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
  }

  .items-table input,
  .items-table textarea {
    border: none !important;
  }

  @page {
    size: A4 portrait;
    margin: 10mm;
  }

  .items-table th {
    background-color: #f0f0f0 !important;
  }

  .remark-input {
    width: 100% !important;
    border: none;
    background: transparent;
  }
}

/* Responsive */
@media screen and (max-width: 800px) {
  .purchase-container {
    margin: 10px;
    padding: 10px;
  }

  .info-row .wide-input,
  .info-row input:not(.wide-input) {
    width: 100%;
  }

  .info-row {
    flex-wrap: wrap;
  }

  .info-row label {
    width: 100%;
    margin-bottom: 2px;
  }
}
</style>
