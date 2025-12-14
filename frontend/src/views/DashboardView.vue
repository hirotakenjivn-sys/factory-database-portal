<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <h1 class="page-title">Dashboard</h1>

      <div class="grid grid-4">
        <div class="card stat-card">
          <h3>Customers</h3>
          <p class="stat-value">{{ stats.customers.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>Products</h3>
          <p class="stat-value">{{ stats.products.toLocaleString() }}</p>
        </div>
        <div class="card stat-card">
          <h3>Processes</h3>
          <p class="stat-value">{{ stats.processes }}</p>
        </div>
        <div class="card stat-card">
          <h3>Count</h3>
          <p class="stat-value">{{ stats.count }}</p>
        </div>
      </div>

      <!-- グラフエリア -->
      <div class="grid grid-2" style="margin-top: var(--spacing-lg)">
        <div class="card">
          <h2>Financial States</h2>
          <Bar v-if="salesChartData" :data="salesChartData" :options="chartOptions" />
        </div>
        <div class="card">
          <h2>Daily Production</h2>
          <Bar v-if="productionChartData" :data="productionChartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Machine Status Section -->
      <div class="machine-status-section">
        <div class="layout-container">
          <img src="@/assets/factory_layout.png" alt="Factory Layout" class="factory-layout" />
        </div>
        <div class="status-table-container">
          <table class="status-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Pressure</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Process</th>
                <th>Qty/Total</th>
                <th>Name</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="machine in machineStatus" :key="machine.no">
                <td>{{ machine.no }}</td>
                <td>{{ machine.pressure }}</td>
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
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../components/common/AppHeader.vue'
import AppNavigation from '../components/common/AppNavigation.vue'
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
  customers: 0,
  products: 0,
  processes: 0,
  count: 0,
})

const machineStatus = ref([
  { no: "'01", pressure: 110, customer: "Tokyo Keiki", product: "SPACERToshibaK9459006P003-BA-PIEC", process: "3/5", qty: "1200/4800", name: "Nguyễn Thị Lan" },
  { no: "'02", pressure: 80, customer: "OTL", product: "BA-13/FIXED CONTACTOR PLATE(RoHS)", process: "5/5", qty: "450/700", name: "None" },
  { no: "'03", pressure: 80, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'04", pressure: 60, customer: "Shengbang", product: "Spacer (P113 TDTK)", process: "2/3", qty: "32000/40000", name: "Lê Minh Đức" },
  { no: "'05", pressure: 60, customer: "Honda", product: "WASHER,PLAIN,8MM", process: "6/7", qty: "1000/1000", name: "None" },
  { no: "'06", pressure: 45, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'07", pressure: 45, customer: "Daiwa", product: "PLATETakakoHOLDER SUCTION", process: "1/1", qty: "100/100", name: "None" },
  { no: "'08", pressure: 45, customer: "Brother", product: "THREAD RELEASE LEVER", process: "7/7", qty: "2000/2000", name: "Đỗ Quang Vinh" },
  { no: "'09", pressure: 45, customer: "F/pan 20", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'10", pressure: 35, customer: "Takazono", product: "DEGUCHI_PURE-TO", process: "5/6", qty: "5000/12500", name: "Hoàng Việt Anh" },
  { no: "'11", pressure: 80, customer: "K.Source", product: "WASHERMitsubaSG03001, TERMINAL", process: "2/7", qty: "150/1500", name: "None" },
  { no: "'12", pressure: 110, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'12-B", pressure: 150, customer: "Meggitt", product: "TOLEFocusBracket FPL30W-NEW", process: "4/7", qty: "50000/50000", name: "None" },
  { no: "'14", pressure: 110, customer: "Kurabe", product: "METAL PLATE Code: 9538252D", process: "1/7", qty: "300/400", name: "Võ Thị Ngọc" },
  { no: "'15", pressure: 110, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'16", pressure: 25, customer: "AMPHENOL", product: "PLAN3564-0047-XXX", process: "5/7", qty: "10000/20000", name: "Nguyễn Văn Dũng" },
  { no: "'17", pressure: 35, customer: "JYS", product: "WASHER-PLAIN", process: "7/7", qty: "2500/3000", name: "None" },
  { no: "'18", pressure: 60, customer: "Fujikura", product: "CFAS2-098C4*3", process: "2/2", qty: "100/200", name: "Phan Anh Khoa" },
  { no: "'19", pressure: 200, customer: "Aiphone", product: "Q.TB-SE SP FIXER", process: "6/7", qty: "800/1000", name: "None" },
  { no: "'21", pressure: 45, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'22", pressure: 200, customer: "Akiba", product: "SHI-BT (910308-B103-003)", process: "1/3", qty: "49000/50000", name: "None" },
  { no: "'23", pressure: 80, customer: "Kyokuto", product: "TAM CO DINH/", process: "3/4", qty: "700/1400", name: "Trần Minh Quân" },
  { no: "'24", pressure: 20, customer: "Panasonic", product: "INSTALL PLATE", process: "5/7", qty: "12000/12000", name: "None" },
  { no: "'25", pressure: 35, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'26", pressure: 80, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'27", pressure: 110, customer: "Aqua", product: "60134942HaradaGUIDE PIPE", process: "6/7", qty: "200/5000", name: "Đặng Hồng Phúc" },
  { no: "'28", pressure: 110, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'30", pressure: 30, customer: "None", product: "None", process: "None", qty: "None", name: "None" },
  { no: "'31", pressure: 60, customer: "TYSLONG", product: "HANDLE PROCESSING", process: "3/7", qty: "500/800", name: "None" },
])

const salesChartData = ref(null)
const productionChartData = ref(null)

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

onMounted(async () => {
  try {
    // 統計カードデータ
    const statsResponse = await api.get('/dashboard/cards')
    stats.value = statsResponse.data

    // Financial States (Dummy Data)
    // const salesResponse = await api.get('/dashboard/sales-weekly')
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

    // 日別生産数データ
    const productionResponse = await api.get('/dashboard/production-daily')
    productionChartData.value = {
      labels: productionResponse.data.map(item => item.date),
      datasets: [
        {
          label: 'Quantity',
          backgroundColor: '#2ecc71',
          borderColor: '#2ecc71',
          data: productionResponse.data.map(item => item.quantity),
        },
      ],
    }
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
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.factory-layout {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
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
</style>
