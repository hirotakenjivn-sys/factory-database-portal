<template>
  <AppLayout>
      <h1 class="page-title">Dashboard</h1>

      <div class="grid grid-4">
        <div class="card stat-card">
          <h3>products</h3>
          <p class="stat-value">{{ stats.products.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>customers</h3>
          <p class="stat-value">{{ stats.customers.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>processes</h3>
          <p class="stat-value">{{ stats.processes.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>count</h3>
          <p class="stat-value">{{ stats.count.toLocaleString() }}</p>
        </div>
      </div>

      <div class="grid grid-4" style="margin-top: var(--spacing-md)">
        <div class="card stat-card">
          <h3>employees</h3>
          <p class="stat-value">{{ stats.employees.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>machine_list</h3>
          <p class="stat-value">{{ stats.machine_list.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>material_rates</h3>
          <p class="stat-value">{{ stats.material_rates.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>factory_db</h3>
          <p class="stat-value">{{ stats.db_size_mb }} MB</p>
        </div>
      </div>

      <!-- グラフエリア -->
      <div class="grid grid-2" style="margin-top: var(--spacing-lg)">
        <div class="card">
          <h2>Financial States</h2>
          <Bar v-if="salesChartData" :data="salesChartData" :options="chartOptions" />
        </div>
        <div class="card calendar-card">
          <div class="calendar-header">
            <button class="btn btn-secondary calendar-nav" @click="prevMonth">&lt;</button>
            <h2 class="calendar-title">{{ monthNames[calendarMonth] }} {{ calendarYear }}</h2>
            <button class="btn btn-secondary calendar-nav" @click="nextMonth">&gt;</button>
          </div>
          <div class="calendar-grid">
            <div class="calendar-day-header" v-for="day in weekDays" :key="day">{{ day }}</div>
            <div
              v-for="(date, index) in calendarDates"
              :key="index"
              :class="getDateClass(date)"
            >
              <span v-if="date">{{ date.getDate() }}</span>
            </div>
          </div>
          <div class="calendar-legend">
            <span class="legend-item"><span class="legend-color holiday-weekly"></span> Weekly</span>
            <span class="legend-item"><span class="legend-color holiday-public"></span> Public</span>
            <span class="legend-item"><span class="legend-color today"></span> Today</span>
          </div>
        </div>
      </div>

      <!-- Machine Status Section -->
      <div class="machine-status-section">
        <div class="layout-container">
          <svg viewBox="0 0 362 432" class="factory-svg" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Factory layout">
            <!-- Areas (static) -->
            <g>
              <rect x="13" y="10" width="179" height="86" class="area"/>
              <text x="102.5" y="53.0" class="area-text">MOLD</text>

              <rect x="222" y="10" width="124" height="115" class="area"/>
              <text x="284.0" y="67.5" class="area-text">Wire cutting room</text>

              <rect x="13" y="110" width="90" height="15" class="area"/>
              <text x="58.0" y="117.5" class="area-text">Milling</text>

              <rect x="13" y="125" width="90" height="31" class="area"/>
              <text x="58.0" y="140.5" class="area-text">CNC Toshiba</text>

              <rect x="13" y="155" width="119" height="30" class="area"/>
              <text x="72.5" y="170.0" class="area-text">Grinding</text>

              <rect x="132" y="110" width="60" height="60" class="area"/>
              <text x="162.0" y="140.0" class="area-text">CNC</text>

              <rect x="132" y="200" width="60" height="45" class="area"/>
              <text x="162.0" y="210.9" class="area-text">
                <tspan x="162.0" y="210.9">molding</tspan>
                <tspan x="162.0" y="223.6">work space</tspan>
              </text>

              <rect x="132" y="275" width="60" height="45" class="area"/>
              <text x="162.0" y="285.9" class="area-text">
                <tspan x="162.0" y="285.9">Mold</tspan>
                <tspan x="162.0" y="298.6">warehouse</tspan>
              </text>
            </g>

            <!-- Tag (static label) -->
            <g>
              <rect x="162" y="170" width="30" height="15" class="tag"/>
              <text x="177.0" y="177.5" class="press-text">PRES</text>
            </g>

            <!-- Presses (Vue reactive) -->
            <g>
              <g v-for="p in presses" :key="p.id" @click="selectPress(p.id)" style="cursor:pointer">
                <rect
                  :x="p.x" :y="p.y" :width="p.w" :height="p.h"
                  :class="['press-rect', 'status-' + pressStatus[p.id], { selected: selectedPressId === pressIdToNo(p.id) }]"
                />
                <text
                  :x="p.tx" :y="p.ty"
                  class="press-text"
                  :font-size="p.fs"
                >{{ p.label }}</text>
              </g>
            </g>
          </svg>
          <div class="svg-legend">
            <span class="svg-legend-item"><span class="svg-legend-box running"></span> Running</span>
            <span class="svg-legend-item"><span class="svg-legend-box idle"></span> Idle</span>
            <span class="svg-legend-item"><span class="svg-legend-box warning"></span> Warning</span>
            <span class="svg-legend-item"><span class="svg-legend-box error"></span> Error</span>
          </div>
          <div class="selected-press-info" v-if="selectedPressId">
            <strong>Press:</strong> {{ selectedPressId }}
          </div>
        </div>
        <div class="status-table-container">
          <table class="status-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Pressure</th>
                <th>LOT, No</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Process</th>
                <th>Qty/Total</th>
                <th>Name</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="machine in machineStatus"
                :key="machine.no"
                :ref="el => { if (el) rowRefs[machine.no] = el }"
                :class="{ 'row-selected': selectedPressId === machine.no }"
              >
                <td>{{ machine.no }}</td>
                <td>{{ machine.pressure }}</td>
                <td>{{ machine.lot_no }}</td>
                <td>{{ machine.customer }}</td>
                <td>{{ machine.product }}</td>
                <td>{{ machine.process }}</td>
                <td>{{ machine.qty }}</td>
                <td>{{ machine.name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import api from '../utils/api'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'

// Chart.jsのコンポーネントを登録
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const stats = ref({
  products: 0,
  customers: 0,
  processes: 0,
  count: 0,
  employees: 0,
  machine_list: 0,
  material_rates: 0,
  db_size_mb: 0,
})

// Machine list — No & Pressure populated, others blank
const machineStatus = ref([
  { no: "01",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "02",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "03",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "04",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "05",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "06",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "07",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "08",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "09",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "10",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "11",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "12",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "12-B", pressure: 150, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "14",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "15",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "16",   pressure: 25,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "17",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "18",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "19",   pressure: 200, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "21",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "22",   pressure: 200, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "23",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "24",   pressure: 20,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "25",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "26",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "27",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "28",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "30",   pressure: 30,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "31",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
])

// Factory SVG layout — presses
const presses = [
  { id: '28',   x: 222, y: 141, w: 30,  h: 15,  tx: 237,   ty: 148.5, fs: 10, label: '28' },
  { id: '18',   x: 252, y: 141, w: 30,  h: 15,  tx: 267,   ty: 148.5, fs: 10, label: '18' },
  { id: '17',   x: 222, y: 170, w: 60,  h: 15,  tx: 252,   ty: 177.5, fs: 10, label: '17' },
  { id: '16',   x: 222, y: 200, w: 60,  h: 15,  tx: 252,   ty: 207.5, fs: 10, label: '16' },
  { id: '15',   x: 222, y: 230, w: 60,  h: 15,  tx: 252,   ty: 237.5, fs: 10, label: '15' },
  { id: '14',   x: 222, y: 260, w: 60,  h: 15,  tx: 252,   ty: 267.5, fs: 10, label: '14' },
  { id: '12-B', x: 222, y: 290, w: 60,  h: 15,  tx: 252,   ty: 297.5, fs: 10, label: '12-B' },
  { id: '12',   x: 222, y: 320, w: 60,  h: 15,  tx: 252,   ty: 327.5, fs: 10, label: '12' },
  { id: '11',   x: 222, y: 348, w: 60,  h: 15,  tx: 252,   ty: 355.5, fs: 10, label: '11' },
  { id: '10',   x: 312, y: 170, w: 34,  h: 15,  tx: 329,   ty: 177.5, fs: 10, label: '10' },
  { id: '9',    x: 312, y: 185, w: 34,  h: 15,  tx: 329,   ty: 192.5, fs: 10, label: '9' },
  { id: '8',    x: 312, y: 200, w: 34,  h: 15,  tx: 329,   ty: 207.5, fs: 10, label: '8' },
  { id: '7',    x: 312, y: 215, w: 34,  h: 15,  tx: 329,   ty: 222.5, fs: 10, label: '7' },
  { id: '6',    x: 312, y: 230, w: 34,  h: 15,  tx: 329,   ty: 237.5, fs: 10, label: '6' },
  { id: '5',    x: 312, y: 260, w: 34,  h: 15,  tx: 329,   ty: 267.5, fs: 10, label: '5' },
  { id: '4',    x: 312, y: 275, w: 34,  h: 15,  tx: 329,   ty: 282.5, fs: 10, label: '4' },
  { id: '3',    x: 312, y: 290, w: 34,  h: 15,  tx: 329,   ty: 297.5, fs: 10, label: '3' },
  { id: '2',    x: 312, y: 320, w: 34,  h: 15,  tx: 329,   ty: 327.5, fs: 10, label: '2' },
  { id: '1',    x: 312, y: 335, w: 34,  h: 13,  tx: 329,   ty: 341.5, fs: 9,  label: '1' },
  { id: '30',   x: 13,  y: 200, w: 30,  h: 60,  tx: 28,    ty: 230,   fs: 13, label: '30' },
  { id: '31',   x: 13,  y: 260, w: 30,  h: 60,  tx: 28,    ty: 290,   fs: 13, label: '31' },
  { id: '24',   x: 13,  y: 320, w: 30,  h: 43,  tx: 28,    ty: 341.5, fs: 13, label: '24' },
  { id: '21',   x: 73,  y: 245, w: 30,  h: 60,  tx: 88,    ty: 275,   fs: 13, label: '21' },
  { id: '25',   x: 73,  y: 305, w: 30,  h: 58,  tx: 88,    ty: 334,   fs: 13, label: '25' },
  { id: '19',   x: 102, y: 215, w: 30,  h: 148, tx: 117,   ty: 289,   fs: 13, label: '19' },
  { id: '23',   x: 132, y: 320, w: 60,  h: 28,  tx: 162,   ty: 334,   fs: 13, label: '23' },
  { id: '22',   x: 102, y: 363, w: 90,  h: 30,  tx: 147,   ty: 378,   fs: 13, label: '22' },
  { id: '27',   x: 222, y: 378, w: 124, h: 15,  tx: 284,   ty: 385.5, fs: 10, label: '27' },
  { id: '26',   x: 222, y: 408, w: 124, h: 15,  tx: 284,   ty: 415.5, fs: 10, label: '26' },
]

// Press status (default all idle)
const pressStatus = reactive(
  Object.fromEntries(presses.map(p => [p.id, 'idle']))
)

const selectedPressId = ref(null)
const rowRefs = reactive({})

// Map SVG press id to table no (e.g. '1' -> '01', '12-B' -> '12-B')
function pressIdToNo(id) {
  if (id.includes('-')) return id
  return id.padStart(2, '0')
}

function selectPress(id) {
  const no = pressIdToNo(id)
  selectedPressId.value = selectedPressId.value === no ? null : no
  if (selectedPressId.value && rowRefs[selectedPressId.value]) {
    nextTick(() => {
      rowRefs[selectedPressId.value]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  }
}

const salesChartData = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top',
    },
  },
}

// Calendar state
const today = new Date()
const calendarYear = ref(today.getFullYear())
const calendarMonth = ref(today.getMonth())
const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const holidays = ref([])

const calendarDates = computed(() => {
  const dates = []
  const firstDay = new Date(calendarYear.value, calendarMonth.value, 1)
  const lastDay = new Date(calendarYear.value, calendarMonth.value + 1, 0)

  const emptySlots = (firstDay.getDay() + 6) % 7
  for (let i = 0; i < emptySlots; i++) {
    dates.push(null)
  }

  for (let d = 1; d <= lastDay.getDate(); d++) {
    dates.push(new Date(calendarYear.value, calendarMonth.value, d))
  }

  return dates
})

const holidayDatesMap = computed(() => {
  const map = new Map()
  holidays.value.forEach(h => {
    const date = new Date(h.date_holiday)
    const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
    map.set(key, h.date_type)
  })
  return map
})

const getHolidayType = (date) => {
  if (!date) return null
  const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
  return holidayDatesMap.value.get(key) || null
}

const isToday = (date) => {
  if (!date) return false
  return date.getFullYear() === today.getFullYear() &&
         date.getMonth() === today.getMonth() &&
         date.getDate() === today.getDate()
}

const getDateClass = (date) => {
  if (!date) return 'calendar-day empty'
  const classes = ['calendar-day']

  const holidayType = getHolidayType(date)
  if (holidayType) {
    if (holidayType === 'Ngày nghỉ hàng tuần') {
      classes.push('holiday-weekly')
    } else {
      classes.push('holiday-public')
    }
  }

  if (isToday(date)) classes.push('today')
  if (date.getDay() === 0) classes.push('sunday')
  if (date.getDay() === 6) classes.push('saturday')
  return classes.join(' ')
}

const prevMonth = () => {
  if (calendarMonth.value === 0) {
    calendarMonth.value = 11
    calendarYear.value--
  } else {
    calendarMonth.value--
  }
}

const nextMonth = () => {
  if (calendarMonth.value === 11) {
    calendarMonth.value = 0
    calendarYear.value++
  } else {
    calendarMonth.value++
  }
}

onMounted(async () => {
  try {
    // Stats card data
    const statsResponse = await api.get('/dashboard/cards')
    stats.value = { ...stats.value, ...statsResponse.data }

    // Financial States (Dummy Data)
    salesChartData.value = {
      labels: ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
      datasets: [
        {
          label: 'Revenue',
          backgroundColor: '#3498db',
          borderColor: '#3498db',
          data: [
            123035353028,
            123951288216,
            139022514385,
            128487074583,
            127743763779,
            144837448872,
            178199346754,
            145636172962,
            165674798218,
            133836603590
          ],
        },
      ],
    }

    // Holiday data for calendar
    const holidayResponse = await api.get('/schedule/calendar')
    holidays.value = holidayResponse.data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-2xl);
}

.stat-card h3 {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--primary);
}

.card h2 {
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.card canvas {
  max-height: 300px;
}

.machine-status-section {
  display: flex;
  gap: 20px;
  margin-top: 30px;
  height: 600px; /* Adjust height as needed */
}

.layout-container {
  flex: 1;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Factory SVG */
.factory-svg {
  width: 100%;
  max-height: 500px;
  background: #fff;
}

.area {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  fill: rgb(183,183,183);
  stroke: rgb(120,120,120);
  stroke-width: 2;
}

.area-text {
  font-family: Arial, sans-serif;
  font-size: 11px;
  fill: #222;
  text-anchor: middle;
  dominant-baseline: middle;
}

.press-rect {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  stroke: rgb(120,120,120);
  stroke-width: 2;
  cursor: pointer;
  transition: fill 0.2s;
}

.press-rect:hover {
  stroke: #0055ff;
  stroke-width: 3;
}

.press-rect.selected {
  stroke: #0055ff;
  stroke-width: 3;
}

.tag {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  fill: rgb(207,226,243);
  stroke: rgb(120,120,120);
  stroke-width: 2;
}

.press-text {
  font-family: Arial, sans-serif;
  font-size: 11px;
  fill: #222;
  text-anchor: middle;
  dominant-baseline: middle;
  pointer-events: none;
}

/* Status colors */
.status-running { fill: #6abf69; }
.status-idle    { fill: rgb(207,226,243); }
.status-error   { fill: #e74c3c; }
.status-warning { fill: #f4d03f; }

/* SVG legend */
.svg-legend {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: #555;
}

.svg-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.svg-legend-box {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  display: inline-block;
}

.svg-legend-box.running { background: #6abf69; }
.svg-legend-box.idle    { background: rgb(207,226,243); }
.svg-legend-box.warning { background: #f4d03f; }
.svg-legend-box.error   { background: #e74c3c; }

.selected-press-info {
  margin-top: 6px;
  font-size: 13px;
  color: #333;
  background: #f0f4f8;
  padding: 6px 14px;
  border-radius: 6px;
}

.status-table-container {
  flex: 1;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: auto; /* Enable scrolling */
}

.status-table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap; /* Prevent wrapping for horizontal scroll */
}

.status-table th,
.status-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.status-table th {
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
}

.status-table tr:hover {
  background-color: #f5f5f5;
}

.status-table tr.row-selected {
  background-color: #d6eaf8;
}

/* Calendar Styles */
.calendar-card {
  padding: var(--spacing-md);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.calendar-title {
  margin: 0;
  min-width: 140px;
  text-align: center;
  font-size: var(--font-size-lg);
}

.calendar-nav {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-base);
  font-weight: bold;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: var(--spacing-sm);
}

.calendar-day-header {
  text-align: center;
  font-weight: 600;
  padding: var(--spacing-xs);
  background: var(--background-secondary);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.calendar-day {
  text-align: center;
  padding: var(--spacing-xs);
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  font-size: var(--font-size-sm);
}

.calendar-day.empty {
  background: transparent;
  border-color: transparent;
}

.calendar-day.holiday-weekly {
  background: #e3f2fd;
  color: #1565c0;
  font-weight: 600;
}

.calendar-day.holiday-public {
  background: #ffebee;
  color: #c62828;
  font-weight: 600;
}

.calendar-day.today {
  border: 2px solid var(--primary);
  font-weight: 700;
}

.calendar-day.sunday {
  color: #c62828;
}

.calendar-day.saturday {
  color: #1565c0;
}

.calendar-legend {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  border: 1px solid var(--border);
}

.legend-color.holiday-weekly {
  background: #e3f2fd;
}

.legend-color.holiday-public {
  background: #ffebee;
}

.legend-color.today {
  border: 2px solid var(--primary);
}
</style>
