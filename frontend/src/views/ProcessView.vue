<template>
  <AppLayout>
    <h1 class="page-title">Process Table</h1>

    <div class="card">
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
        <table class="table process-table" :style="{ width: tableWidth + 'px' }">
          <thead>
            <tr>
              <th class="sticky-col resizable-col" :style="{ width: colWidths.customer + 'px' }">
                Customer Name
                <span class="resize-handle" @mousedown.prevent="startResize($event, 'customer')"></span>
              </th>
              <th class="sticky-col-2 resizable-col" :style="{ width: colWidths.product + 'px', left: colWidths.customer + 'px' }">
                Product Code
                <span class="resize-handle" @mousedown.prevent="startResize($event, 'product')"></span>
              </th>
              <th v-for="i in 20" :key="i">Process {{ i }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProcessTable" :key="product.product_id">
              <td class="sticky-col" :style="{ width: colWidths.customer + 'px' }">{{ product.customer_name }}</td>
              <td class="sticky-col-2" :style="{ width: colWidths.product + 'px', left: colWidths.customer + 'px' }">
                {{ product.product_code }}
              </td>
              <td
                v-for="i in 20"
                :key="i"
                :class="{
                  'error-cell': isPressSetIncomplete(product, product[`process_${i}`]),
                  'highlight-zero-cycletime': product[`process_${i}`] && Number(product[`rough_cycletime_${i}`]) === 0
                }"
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
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import api from '../utils/api'

const searchTable = ref({
  customer_name: '',
  product_code: ''
})

const showOnlyHighlighted = ref(false)

const colWidths = ref({
  customer: 130,
  product: 180,
})

const tableWidth = computed(() => colWidths.value.customer + colWidths.value.product + 20 * 100)

// Column resize logic
let resizingCol = null
let resizeStartX = 0
let resizeStartWidth = 0

const startResize = (event, col) => {
  resizingCol = col
  resizeStartX = event.clientX
  resizeStartWidth = colWidths.value[col]
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

const onResize = (event) => {
  if (!resizingCol) return
  const diff = event.clientX - resizeStartX
  const newWidth = Math.max(60, resizeStartWidth + diff)
  colWidths.value[resizingCol] = newWidth
}

const stopResize = () => {
  resizingCol = null
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
})

const processTable = ref([])

const hasHighlight = (product) => {
  for (let i = 1; i <= 20; i++) {
    if (product[`process_${i}`] && Number(product[`rough_cycletime_${i}`]) === 0) {
      return true
    }
  }
  return false
}

const filteredProcessTable = computed(() => {
  let result = processTable.value.filter(product => {
    const customerMatch = !searchTable.value.customer_name ||
      product.customer_name.toLowerCase().includes(searchTable.value.customer_name.toLowerCase())
    const productMatch = !searchTable.value.product_code ||
      product.product_code.toLowerCase().includes(searchTable.value.product_code.toLowerCase())
    const highlightMatch = !showOnlyHighlighted.value || hasHighlight(product)
    return customerMatch && productMatch && highlightMatch
  })

  result.sort((a, b) => {
    const aHas = hasHighlight(a) ? 1 : 0
    const bHas = hasHighlight(b) ? 1 : 0
    return bHas - aHas
  })

  return result
})

const loadProcessTable = async () => {
  try {
    const response = await api.get('/press/process-table')
    processTable.value = response.data
  } catch (error) {
    console.error('Failed to load process table:', error)
  }
}

const isPressSetIncomplete = (product, processName) => {
  if (!processName) return false

  const match = processName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
  if (!match) return false

  const denominator = parseInt(match[2], 10)
  if (denominator <= 0) return true

  const existingParts = new Set()

  for (let i = 1; i <= 20; i++) {
    const pName = product[`process_${i}`]
    if (pName) {
      const pMatch = pName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
      if (pMatch) {
        const pNum = parseInt(pMatch[1], 10)
        const pDenom = parseInt(pMatch[2], 10)
        if (pDenom === denominator) {
          existingParts.add(pNum)
        }
      }
    }
  }

  for (let i = 1; i <= denominator; i++) {
    if (!existingParts.has(i)) {
      return true
    }
  }

  return false
}

onMounted(() => {
  loadProcessTable()
})
</script>

<style scoped>
:deep(.app-main) {
  max-width: 100%;
}

.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.table-scroll-container {
  overflow-x: auto;
  max-width: 100%;
}

.process-table {
  table-layout: fixed;
}

.process-table th,
.process-table td {
  width: 100px;
  white-space: nowrap;
  box-sizing: border-box;
}

.process-table .sticky-col,
.process-table .sticky-col-2 {
  max-width: none;
}

.sticky-col,
.sticky-col-2 {
  position: sticky;
  background: white;
  z-index: 2;
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sticky-col {
  left: 0;
}

.sticky-col-2 {
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.process-table thead .sticky-col,
.process-table thead .sticky-col-2 {
  background: #f8f9fa;
}

.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  height: 100%;
  cursor: col-resize;
  background: transparent;
}

.resize-handle:hover {
  background: var(--primary);
  opacity: 0.3;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.error-cell {
  background-color: #ffcccc !important;
}

.highlight-zero-cycletime {
  background-color: rgba(255, 235, 59, 0.3) !important;
}
</style>
