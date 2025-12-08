<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <h1 class="page-title">ダッシュボード</h1>

      <div class="grid grid-4">
        <div class="card stat-card">
          <h3>PO売上（過去30日）</h3>
          <p class="stat-value">{{ stats.total_sales.toLocaleString() }} 個</p>
        </div>
        <div class="card stat-card">
          <h3>本日生産数</h3>
          <p class="stat-value">{{ stats.today_production.toLocaleString() }} pcs</p>
        </div>
        <div class="card stat-card">
          <h3>金型故障中件数</h3>
          <p class="stat-value">{{ stats.broken_molds }} 件</p>
        </div>
        <div class="card stat-card">
          <h3>遅延件数</h3>
          <p class="stat-value">{{ stats.delayed }} 件</p>
        </div>
      </div>

      <!-- グラフエリア -->
      <div class="grid grid-2" style="margin-top: var(--spacing-lg)">
        <div class="card">
          <h2>週別売上推移</h2>
          <Line v-if="salesChartData" :data="salesChartData" :options="chartOptions" />
        </div>
        <div class="card">
          <h2>日別生産数</h2>
          <Bar v-if="productionChartData" :data="productionChartData" :options="chartOptions" />
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
  total_sales: 0,
  today_production: 0,
  broken_molds: 0,
  delayed: 0,
})

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

    // 週別売上データ
    const salesResponse = await api.get('/dashboard/sales-weekly')
    salesChartData.value = {
      labels: salesResponse.data.map(item => `Week ${item.week}`),
      datasets: [
        {
          label: '売上数量',
          backgroundColor: '#3498db',
          borderColor: '#3498db',
          data: salesResponse.data.map(item => item.quantity),
        },
      ],
    }

    // 日別生産数データ
    const productionResponse = await api.get('/dashboard/production-daily')
    productionChartData.value = {
      labels: productionResponse.data.map(item => item.date),
      datasets: [
        {
          label: '生産数',
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
</style>
