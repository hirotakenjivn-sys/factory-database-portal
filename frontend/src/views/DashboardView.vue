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

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
