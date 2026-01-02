<template>
  <AppLayout>
    <!-- エラーダイアログ -->
    <ErrorDialog
      :show="showErrorDialog"
      :title="errorDialogTitle"
      :message="errorDialogMessage"
      @close="closeErrorDialog"
    />

      <h1 class="page-title">スケジュール - 生産計画</h1>

      <!-- 工場稼働時間入力 -->
      <div class="working-hours-top">
        <label class="working-hours-label">工場稼働時間（h）</label>
        <input
          v-model.number="workingHours"
          class="working-hours-input-compact"
          type="number"
          min="8"
          max="12"
          step="1"
        />
      </div>

      <!-- タブナビゲーション -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'productionPlan'"
          :class="{ active: activeTab === 'productionPlan' }"
          class="tab-btn"
        >
          全体生産計画
        </button>
        <button
          @click="activeTab = 'pressPlan'"
          :class="{ active: activeTab === 'pressPlan' }"
          class="tab-btn"
        >
          今週のプレス計画
        </button>
        <button
          @click="activeTab = 'progress'"
          :class="{ active: activeTab === 'progress' }"
          class="tab-btn"
        >
          進捗確認
        </button>
        <button
          @click="activeTab = 'progress2'"
          :class="{ active: activeTab === 'progress2' }"
          class="tab-btn"
        >
          進捗確認２
        </button>
      </div>

      <!-- 進捗確認タブ -->
      <div v-if="activeTab === 'progress'" class="card">
        <h2>進捗確認</h2>

        <!-- 検索フィールド -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">顧客名</label>
            <input v-model="searchProgress.customer_name" class="form-input" type="text" placeholder="顧客名で検索..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">製品コード</label>
            <input v-model="searchProgress.product_code" class="form-input" type="text" placeholder="製品コードで検索..." />
          </div>
        </div>

        <div class="table-scroll-container">
          <table class="table process-table">
            <thead>
              <tr>
                <th class="sticky-col">顧客名</th>
                <th class="sticky-col-2">製品コード</th>
                <th class="sticky-col-3">PO数量合計</th>
                <th class="sticky-col-4">PO No.</th>
                <th class="sticky-col-5">納期</th>
                <th v-for="i in 20" :key="i">工程{{ i }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProgressTable" :key="product.product_id">
                <td class="sticky-col">{{ product.customer_name }}</td>
                <td class="sticky-col-2">
                  <CopyableText :text="product.product_code" />
                </td>
                <td class="sticky-col-3 process-cell">
                  <span v-if="product.total_po_quantity">
                    {{ product.total_po_quantity.toLocaleString() }}<br>({{ product.total_processing_time }})
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="sticky-col-4">
                  <div v-html="product.po_numbers_display"></div>
                </td>
                <td class="sticky-col-5">{{ product.earliest_delivery_date || '-' }}</td>
                <td
                  v-for="i in 20"
                  :key="i"
                  :class="{
                    'clickable-cell': product[`process_${i}`],
                    'error-cell': isPressSetIncomplete(product, product[`process_${i}`]),
                    'text-danger': isProcessDelayed(product[`process_${i}`], product.production_deadline)
                  }"
                  @click="showTraceCard(product, i)"
                  class="process-cell"
                >
                  <div v-if="product[`process_${i}`]">
                    <div>{{ product[`process_${i}`].name }}</div>
                    <div class="process-time-info">{{ product[`process_${i}`].date }}</div>
                    <div class="process-time-info">{{ product[`process_${i}`].value }}{{ product[`process_${i}`].unit }}</div>
                  </div>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredProgressTable.length === 0" class="empty-state">
          <p>データがありません</p>
        </div>
      </div>

      <div v-if="activeTab === 'progress2'" class="card">
        <h2>進捗確認２（プレス機制約なし）</h2>

        <!-- 検索フィールド -->
        <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">顧客名</label>
            <input v-model="searchProgress2.customer_name" class="form-input" type="text" placeholder="顧客名で検索..." />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">製品コード</label>
            <input v-model="searchProgress2.product_code" class="form-input" type="text" placeholder="製品コードで検索..." />
          </div>
        </div>

        <div class="table-scroll-container">
          <table class="table process-table">
            <thead>
              <tr>
                <th class="sticky-col">顧客名</th>
                <th class="sticky-col-2">製品コード</th>
                <th class="sticky-col-3">PO数量合計</th>
                <th class="sticky-col-4">PO No.</th>
                <th class="sticky-col-5">納期</th>
                <th v-for="i in 20" :key="i">工程{{ i }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProgressTable2" :key="product.product_id">
                <td class="sticky-col">{{ product.customer_name }}</td>
                <td class="sticky-col-2">
                  <CopyableText :text="product.product_code" />
                </td>
                <td class="sticky-col-3 process-cell">
                  <span v-if="product.total_po_quantity">
                    {{ product.total_po_quantity.toLocaleString() }}<br>({{ product.total_processing_time }})
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="sticky-col-4">
                  <div v-html="product.po_numbers_display"></div>
                </td>
                <td class="sticky-col-5">{{ product.earliest_delivery_date || '-' }}</td>
                <td
                  v-for="i in 20"
                  :key="i"
                  :class="{
                    'clickable-cell': product[`process_${i}`],
                    'error-cell': isPressSetIncomplete(product, product[`process_${i}`]),
                    'text-danger': isProcessDelayed(product[`process_${i}`], product.production_deadline)
                  }"
                  @click="showTraceCard(product, i)"
                  class="process-cell"
                >
                  <div v-if="product[`process_${i}`]">
                    <div>{{ product[`process_${i}`].name }}</div>
                    <div class="process-time-info">{{ product[`process_${i}`].date }}</div>
                    <div class="process-time-info">{{ product[`process_${i}`].value }}{{ product[`process_${i}`].unit }}</div>
                  </div>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredProgressTable2.length === 0" class="empty-state">
          <p>データがありません</p>
        </div>
      </div>

      <!-- 全体生産計画タブ -->
      <div v-if="activeTab === 'productionPlan'" class="card">
        <h2>全体生産計画</h2>

        <div class="info-box" style="margin-bottom: var(--spacing-md);">
          <p><strong>機能説明:</strong></p>
          <ul style="margin: 8px 0; padding-left: 20px;">
            <li>今週のPOをもとに全工程の生産計画を計算</li>
            <li>プレス工程が連続し機械が異なる場合は並列実行を考慮</li>
            <li>段取り時間60分を適用</li>
            <li>生産締切日・総加工時間（DD"day"HH"hour"形式）を表示</li>
          </ul>
        </div>

        <!-- 計算ボタン -->
        <div class="calculate-section">
          <button @click="generateComprehensivePlan" class="calculate-btn" :disabled="loadingComprehensive">
            <span class="calculate-icon">⚙️</span>
            {{ loadingComprehensive ? '計算中...' : '全体生産計画を計算' }}
          </button>
        </div>

        <!-- ローディング中 -->
        <div v-if="loadingComprehensive" class="progress-section">
          <p class="progress-text">{{ loadingMessage }}</p>
        </div>

        <!-- 全体生産計画結果 -->
        <div v-if="comprehensivePlan.products && comprehensivePlan.products.length > 0" class="comprehensive-plan-results" style="margin-top: var(--spacing-xl);">
          <h3>全体生産計画結果</h3>

          <div style="margin-bottom: 8px;">
            <strong>製品数:</strong> {{ comprehensivePlan.products_count }}件
            <span v-if="comprehensivePlan.schedules_count" style="margin-left: 16px;">
              <strong>スケジュール件数:</strong> {{ comprehensivePlan.schedules_count }}件
            </span>
            <span v-if="comprehensivePlan.makespan" style="margin-left: 16px;">
              <strong>完了予定:</strong> {{ formatScheduleDateTime(comprehensivePlan.makespan) }}
            </span>
          </div>

          <!-- 検索フィルタ -->
          <div style="display: flex; gap: 8px; margin-bottom: var(--spacing-md);">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">顧客名</label>
              <input v-model="searchComprehensive.customer_name" class="form-input" type="text" placeholder="顧客名で検索..." />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">製品コード</label>
              <input v-model="searchComprehensive.product_code" class="form-input" type="text" placeholder="製品コードで検索..." />
            </div>
          </div>

          <!-- 製品ごとのサマリーテーブル -->
          <div class="table-scroll-container">
            <table class="table">
              <thead>
                <tr>
                  <th>顧客名</th>
                  <th>製品コード</th>
                  <th>PO番号</th>
                  <th>PO数量</th>
                  <th>工程数</th>
                  <th>総加工時間</th>
                  <th>生産締切日</th>
                  <th>納期</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in filteredComprehensivePlan" :key="product.product_code">
                  <td>{{ product.customer_name }}</td>
                  <td>
                    <CopyableText :text="product.product_code" />
                  </td>
                  <td>{{ product.po_number }}</td>
                  <td>{{ product.total_quantity.toLocaleString() }}</td>
                  <td>{{ product.process_count }}</td>
                  <td><strong>{{ product.display_string }}</strong></td>
                  <td :class="{
                    'delayed-datetime': new Date(product.production_deadline) < new Date()
                  }">
                    {{ formatScheduleDate(product.production_deadline) }}
                    <span style="font-size: 0.85em; margin-left: 4px;">
                      ({{ getDaysDifference(product.production_deadline) }})
                    </span>
                  </td>
                  <td>{{ formatScheduleDate(product.delivery_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 今週のプレス計画タブ -->
      <div v-if="activeTab === 'pressPlan'" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md);">
          <h2 style="margin-bottom: 0;">今週のプレス計画</h2>
          <button @click="isSimpleView = !isSimpleView" class="btn btn-secondary">
            <span class="calculate-icon">👁️</span>
            {{ isSimpleView ? '詳細表示' : '簡易表示' }}
          </button>
        </div>

        <!-- ローディング中 -->
        <div v-if="loadingPressSchedule" class="progress-section">
          <p class="progress-text">{{ loadingMessage }}</p>
        </div>

        <!-- プレス計画テーブル -->
        <div v-if="pressSchedule.machines && pressSchedule.machines.length > 0" class="press-schedule-container" style="margin-top: 0;">
          <div class="table-scroll-container">
            <table class="table press-schedule-table">
              <thead>
                <tr>
                  <th class="sticky-col-press">機械番号</th>
                  <th v-for="dateStr in pressSchedule.dates" :key="dateStr" style="text-align: center;">
                    <div>{{ formatDateHeader(dateStr) }}</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 4px;">
                      稼働: {{ calculateDailyWorkingHours(dateStr) }}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="machine in pressSchedule.machines" :key="machine.machine_no">
                  <td class="sticky-col-press machine-cell">{{ machine.machine_no }}</td>
                  <td v-for="dateStr in pressSchedule.dates" :key="dateStr" class="schedule-cell">
                    <div v-if="pressSchedule.schedule[machine.machine_no][dateStr].length > 0" class="task-list">
                      <div v-for="(task, idx) in pressSchedule.schedule[machine.machine_no][dateStr]" :key="idx"
                           :class="['task-item', { 'task-item-split': task.is_split, 'task-item-overdue': isTaskOverdue(task) }]">
                        <!-- 簡易表示 -->
                        <div v-if="isSimpleView">
                          <div class="task-header" style="margin-bottom: 2px;">
                            <strong>{{ task.product_code }}</strong>
                            <span class="task-process-name" style="margin-left: 4px; font-size: 10px; padding: 1px 3px;">{{ task.process_name }}</span>
                          </div>
                          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #424242;">
                            <span>{{ task.start_time }}-{{ task.end_time }}</span>
                            <span>
                              <span :class="{ 'quantity-split': task.split_info }">{{ task.day_quantity.toLocaleString() }}</span>/<span>{{ task.po_quantity.toLocaleString() }}</span>
                            </span>
                          </div>
                        </div>

                        <!-- 詳細表示 -->
                        <div v-else>
                          <div class="task-header">
                            <strong>{{ task.product_code }}</strong>
                            <span v-if="task.split_info" class="split-badge">{{ task.split_info }}日目</span>
                            <span class="task-time">{{ task.start_time }} - {{ task.end_time }}</span>
                          </div>
                          <div class="task-time-info">
                            (加工{{ formatProcessingTime(task.setup_time + task.processing_time) }})
                          </div>
                          <div class="task-process-name">
                            工程: {{ task.process_name }}
                          </div>
                          <div class="task-details">
                            <div>顧客: {{ task.customer_name }}</div>
                            <div>数量: <span :class="{ 'quantity-split': task.split_info }">{{ task.day_quantity.toLocaleString() }}</span>/{{ task.po_quantity.toLocaleString() }}</div>
                            <div>納期: {{ task.delivery_date }}</div>
                            <div>生産締切: {{ task.production_deadline }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="empty-cell">-</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- データがない場合 -->
        <div v-if="!loadingPressSchedule && pressSchedule.machines && pressSchedule.machines.length === 0" class="empty-state">
          <p>PRESSマシンが登録されていません、またはスケジュールが生成されていません。</p>
          <p>「全体生産計画」タブで計画を計算してください。</p>
        </div>
      </div>

      <!-- トレースカード（モーダル） -->
      <div v-if="showTraceModal" class="modal-overlay" @click="closeTraceModal">
        <div class="modal-card" @click.stop>
          <div class="modal-header">
            <h3>{{ selectedTrace.product_code }} - {{ selectedTrace.process_name }}</h3>
            <button @click="closeTraceModal" class="modal-close">×</button>
          </div>
          <div class="modal-body">
            <!-- ローディング中 -->
            <div v-if="loadingTraces" style="text-align: center; padding: 20px;">
              <p>トレースデータを読み込み中...</p>
            </div>

            <!-- トレースデータが空 -->
            <div v-else-if="!traces || traces.length === 0" style="text-align: center; padding: 20px; color: #666;">
              <p>未完了のトレースはありません</p>
            </div>

            <!-- トレースデータ表示 -->
            <div v-else class="table-scroll-container" style="max-height: 500px;">
              <table class="table">
                <thead>
                  <tr>
                    <th>登録日時</th>
                    <th>製品番号</th>
                    <th>ロット番号</th>
                    <th>工程名</th>
                    <th>作業者</th>
                    <th>OK数量</th>
                    <th>NG数量</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trace in traces" :key="trace.stamp_trace_id">
                    <td>{{ formatTraceDateTime(trace.timestamp) }}</td>
                    <td>
                      <CopyableText :text="trace.product_code" />
                    </td>
                    <td>{{ trace.lot_number || '-' }}</td>
                    <td>{{ trace.process_name || '-' }}</td>
                    <td>{{ trace.employee_name || '-' }}</td>
                    <td class="number">{{ trace.ok_quantity }}</td>
                    <td class="number">{{ trace.ng_quantity }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import CopyableText from '../components/common/CopyableText.vue'
import ErrorDialog from '../components/common/ErrorDialog.vue'
import api from '../utils/api'
import { formatDateForDisplay } from '../utils/dateFormat'

const activeTab = ref('productionPlan')

// 進捗確認用データ
const progressTable = ref([])
const searchProgress = ref({
  customer_name: '',
  product_code: ''
})

// 進捗確認２用データ（プレス機制約なし）
const progressTable2 = ref([])
const searchProgress2 = ref({
  customer_name: '',
  product_code: ''
})

// 工場稼働時間
const workingHours = ref(8)

// プレス計画用データ
const loadingPressSchedule = ref(false)
const loadingMessage = ref('読み込み中...')
const isSimpleView = ref(false)
const pressSchedule = ref({
  dates: [],
  machines: [],
  schedule: {}
})

// 全体生産計画用データ
const comprehensivePlan = ref({
  products: [],
  schedules_count: 0,
  products_count: 0,
  makespan: null
})
const loadingComprehensive = ref(false)
const searchComprehensive = ref({
  customer_name: '',
  product_code: '',
  process_name: ''
})
const generatedSchedule = ref([])
const searchFullSchedule = ref({
  customer_name: '',
  product_code: '',
  process_name: '',
  status: ''
})

// モーダル関連
const showTraceModal = ref(false)
const selectedTrace = ref({})
const traces = ref([])
const loadingTraces = ref(false)

// エラーダイアログ関連
const showErrorDialog = ref(false)
const errorDialogTitle = ref('エラー')
const errorDialogMessage = ref('')

const showError = (message, title = 'エラー') => {
  errorDialogMessage.value = message
  errorDialogTitle.value = title
  showErrorDialog.value = true
}

const closeErrorDialog = () => {
  showErrorDialog.value = false
}

// 進捗確認テーブルのフィルタリング
const filteredProgressTable = computed(() => {
  return progressTable.value.filter(product => {
    const customerMatch = !searchProgress.value.customer_name ||
      product.customer_name.toLowerCase().includes(searchProgress.value.customer_name.toLowerCase())
    const productMatch = !searchProgress.value.product_code ||
      product.product_code.toLowerCase().includes(searchProgress.value.product_code.toLowerCase())
    return customerMatch && productMatch
  })
})

// 進捗確認２テーブルのフィルタリング
const filteredProgressTable2 = computed(() => {
  return progressTable2.value.filter(product => {
    const customerMatch = !searchProgress2.value.customer_name ||
      product.customer_name.toLowerCase().includes(searchProgress2.value.customer_name.toLowerCase())
    const productMatch = !searchProgress2.value.product_code ||
      product.product_code.toLowerCase().includes(searchProgress2.value.product_code.toLowerCase())
    return customerMatch && productMatch
  })
})

// 全工程スケジュールのフィルタリング
const filteredFullSchedule = computed(() => {
  return generatedSchedule.value.filter(schedule => {
    const customerMatch = !searchFullSchedule.value.customer_name ||
      (schedule.customer_name && schedule.customer_name.toLowerCase().includes(searchFullSchedule.value.customer_name.toLowerCase()))
    const productMatch = !searchFullSchedule.value.product_code ||
      (schedule.product_code && schedule.product_code.toLowerCase().includes(searchFullSchedule.value.product_code.toLowerCase()))
    const processMatch = !searchFullSchedule.value.process_name ||
      (schedule.process_name && schedule.process_name.toLowerCase().includes(searchFullSchedule.value.process_name.toLowerCase()))
    const statusMatch = !searchFullSchedule.value.status ||
      schedule.status === searchFullSchedule.value.status
    return customerMatch && productMatch && processMatch && statusMatch
  })
})

// 生産計画日時の状態を判定（遅延・警告・正常）
const getDatetimeStatus = (plannedDatetime) => {
  if (!plannedDatetime) return 'normal'

  // DD/MM/YYYY HH:MM 形式をパース
  const parts = plannedDatetime.split(' ')
  if (parts.length !== 2) return 'normal'

  const dateParts = parts[0].split('/')
  const timeParts = parts[1].split(':')

  if (dateParts.length !== 3 || timeParts.length !== 2) return 'normal'

  // Date オブジェクトを作成（月は0-indexedなので-1）
  const plannedDate = new Date(
    parseInt(dateParts[2]), // year
    parseInt(dateParts[1]) - 1, // month
    parseInt(dateParts[0]), // day
    parseInt(timeParts[0]), // hour
    parseInt(timeParts[1]) // minute
  )

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const twoDaysLater = new Date(today)
  twoDaysLater.setDate(today.getDate() + 2)
  const fiveDaysLater = new Date(today)
  fiveDaysLater.setDate(today.getDate() + 5)

  // 過去の日時: 赤
  if (plannedDate < now) {
    return 'delayed'
  }
  // 今日+2日まで: 黄色
  else if (plannedDate <= twoDaysLater) {
    return 'warning'
  }
  // +5日まで: 緑
  else if (plannedDate <= fiveDaysLater) {
    return 'normal-green'
  }
  // それ以降: 通常
  else {
    return 'normal'
  }
}

// 進捗確認データを読み込み（使用しない - プレス計画から生成）
// const loadProgressTable = async () => {
//   try {
//     const response = await api.get('/schedule/progress-table')
//     progressTable.value = response.data
//   } catch (error) {
//     console.error('Failed to load progress table:', error)
//   }
// }

// トレースカードを表示（進捗確認タブ用）
const showTraceCard = async (product, processNo) => {
  if (!product[`process_${processNo}`]) {
    return
  }

  const processInfo = product[`process_${processNo}`]
  const processName = processInfo.name

  selectedTrace.value = {
    product_code: product.product_code,
    process_name: processName,
    product_id: product.product_id,
    process_no: processNo
  }

  // トレースデータを取得
  await loadIncompleteTraces(product.product_code)

  showTraceModal.value = true
}

// トレースカードを表示（生産計画タブ用）
const showTraceCardFromPlan = async (planItem) => {
  selectedTrace.value = {
    product_code: planItem.product_code,
    process_name: planItem.process_name,
    customer_name: planItem.customer_name,
    po_quantity: planItem.po_quantity,
    planned_datetime: planItem.planned_datetime
  }

  showTraceModal.value = true
}

// 未完了トレースを読み込む
const loadIncompleteTraces = async (productCode) => {
  loadingTraces.value = true
  traces.value = []

  try {
    const response = await api.get('/trace/incomplete-traces', {
      params: {
        product_code: productCode
      }
    })
    traces.value = response.data
  } catch (error) {
    console.error('トレースデータの取得に失敗しました:', error)
    traces.value = []
  } finally {
    loadingTraces.value = false
  }
}

const closeTraceModal = () => {
  showTraceModal.value = false
  traces.value = []
}

// トレース日時のフォーマット
const formatTraceDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-'
  const date = new Date(dateTimeString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}`
}

// 全工程スケジュールから進捗確認データを生成
const generateProgressFromAllSchedule = async () => {
  try {
    const response = await api.get('/schedule/all-schedule-from-plan', {
      params: {
        working_hours: workingHours.value
      }
    })

    const products = response.data.products

    console.log('API Response products:', products)

    if (!products || products.length === 0) {
      progressTable.value = []
      return
    }

    // progressTable形式に変換
    const progressData = []

    products.forEach(product => {
      console.log('Processing product:', product.product_code, 'total_processing_time:', product.total_processing_time, 'processes:', product.processes)
      const productEntry = {
        customer_name: product.customer_name,
        product_code: product.product_code,
        total_po_quantity: product.po_quantity,
        total_processing_time: product.total_processing_time || '', // バックエンドから取得
        po_numbers_display: product.po_numbers_display || '-', // バックエンドから取得
        earliest_delivery_date: product.delivery_date
      }

      // 工程リストを process_1, process_2, ... に展開（オブジェクト形式）
      // process_noでソート
      const processList = Object.values(product.processes).sort((a, b) => a.process_no - b.process_no)
      console.log('Process list for', product.product_code, ':', processList)
      processList.forEach((processData, index) => {
        const processEntry = {
          name: processData.name,
          date: processData.date,
          value: processData.display_value,
          unit: processData.display_unit,
          latest_end_date: processData.latest_end_date
        }
        console.log(`process_${index + 1}:`, processEntry)
        productEntry[`process_${index + 1}`] = processEntry
      })

      console.log('Final productEntry:', productEntry)
      progressData.push(productEntry)
    })

    // 製品コードでソート
    progressData.sort((a, b) => a.product_code.localeCompare(b.product_code))

    progressTable.value = progressData
  } catch (error) {
    console.error('Failed to generate progress from all schedule:', error)
    progressTable.value = []
  }
}

// 進捗確認２用：プレス機制約なしのスケジュールを取得
const loadProgressSchedule2 = async () => {
  try {
    const response = await api.get('/schedule/unconstrained-schedule', {
      params: {
        working_hours: workingHours.value
      }
    })

    const products = response.data.products

    if (!products || products.length === 0) {
      progressTable2.value = []
      return
    }

    // progressTable2形式に変換
    const progressData = []

    products.forEach(product => {
      const productEntry = {
        customer_name: product.customer_name,
        product_code: product.product_code,
        total_po_quantity: product.po_quantity,
        total_processing_time: product.total_processing_time || '',
        po_numbers_display: product.po_numbers_display || '-',
        earliest_delivery_date: product.delivery_date
      }

      // 工程リストを process_1, process_2, ... に展開
      const processList = Object.values(product.processes).sort((a, b) => a.process_no - b.process_no)
      processList.forEach((processData, index) => {
        const processEntry = {
          name: processData.name,
          date: processData.date,
          value: processData.display_value,
          unit: processData.display_unit,
          latest_end_date: processData.latest_end_date
        }
        productEntry[`process_${index + 1}`] = processEntry
      })

      progressData.push(productEntry)
    })

    // 製品コードでソート
    progressData.sort((a, b) => a.product_code.localeCompare(b.product_code))

    progressTable2.value = progressData
  } catch (error) {
    console.error('Failed to load unconstrained schedule:', error)
    progressTable2.value = []
  }
}

// 工程が遅れているかどうかを判定
const isProcessDelayed = (process, productionDeadline) => {
  if (!process || !process.latest_end_date || !productionDeadline) return false

  try {
    // productionDeadline format: "dd/mm/yyyy"
    const dateParts = productionDeadline.split('/')
    if (dateParts.length !== 3) return false

    // 締切日の終了時刻（23:59:59）を基準にする
    const deadlineDate = new Date(
      parseInt(dateParts[2]), // year
      parseInt(dateParts[1]) - 1, // month
      parseInt(dateParts[0]), // day
      23, 59, 59
    )

    const endDate = new Date(process.latest_end_date)

    return endDate > deadlineDate
  } catch (error) {
    console.error('Failed to compare dates:', error)
    return false
  }
}

// 生成された生産計画から今週のプレス計画を表示
const loadPressScheduleFromPlan = async () => {
  loadingPressSchedule.value = true
  loadingMessage.value = '今週のプレス計画を読み込み中...'

  try {
    const response = await api.get('/schedule/press-weekly-schedule-from-plan', {
      params: {
        working_hours: workingHours.value
      }
    })
    pressSchedule.value = response.data

    if (response.data.machines.length === 0) {
      showError('PRESS機が登録されていません', '警告')
    } else {
      // スケジュールの件数をカウント
      let scheduleCount = 0
      for (const machineNo in response.data.schedule) {
        for (const dateStr in response.data.schedule[machineNo]) {
          scheduleCount += response.data.schedule[machineNo][dateStr].length
        }
      }

      if (scheduleCount === 0) {
        showError('今週のPRESS工程スケジュールがありません。\n先に「生産計画スケジュール」タブで計画を生成してください。', '警告')
      }
    }

    // 全工程から進捗確認データを生成
    await generateProgressFromAllSchedule()
  } catch (error) {
    console.error('Failed to load press schedule from plan:', error)
    showError('プレス計画の読み込みに失敗しました: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingPressSchedule.value = false
    loadingMessage.value = '読み込み中...'
  }
}

// 日付ヘッダーをフォーマット（YYYY-MM-DD → DD/MM (曜日)）
const formatDateHeader = (dateStr) => {
  const date = new Date(dateStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  const weekday = weekdays[date.getDay()]

  return `${day}/${month} (${weekday})`
}

// その日使用するすべてのプレス機の稼働時間合計を計算
const calculateDailyWorkingHours = (dateStr) => {
  if (!pressSchedule.value.schedule || !pressSchedule.value.machines) {
    return '0分'
  }

  let totalMinutes = 0

  // 全プレス機のその日のタスクを集計
  pressSchedule.value.machines.forEach(machine => {
    const tasks = pressSchedule.value.schedule[machine.machine_no]?.[dateStr] || []
    tasks.forEach(task => {
      totalMinutes += (task.setup_time || 0) + (task.processing_time || 0)
    })
  })

  return formatProcessingTime(totalMinutes)
}

// 加工時間をフォーマット（分 → 時間・分表記）
const formatProcessingTime = (minutes) => {
  if (!minutes || minutes === 0) return '0分'

  const totalMinutes = Math.round(minutes)
  const hours = Math.floor(totalMinutes / 60)
  const mins = totalMinutes % 60

  if (hours > 0 && mins > 0) {
    return `${hours}時間${mins}分`
  } else if (hours > 0) {
    return `${hours}時間`
  } else {
    return `${mins}分`
  }
}

// スケジュール日時をフォーマット（dd/mm/yyyy hh:mm形式）
const formatScheduleDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}

// スケジュール日付をフォーマット（dd/mm/yyyy形式）
const formatScheduleDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

// 状態ラベルを取得
const getStatusLabel = (status) => {
  const labels = {
    scheduled: '予定',
    waiting: '待機中',
    in_progress: '進行中',
    completed: '完了'
  }
  return labels[status] || status
}

// 状態クラスを取得
const getStatusClass = (status) => {
  return `status-badge status-${status}`
}

// スケジュール行のクラスを取得
const getScheduleRowClass = (schedule) => {
  if (schedule.status === 'waiting') return 'schedule-row-waiting'
  if (schedule.status === 'in_progress') return 'schedule-row-progress'
  if (schedule.status === 'completed') return 'schedule-row-completed'
  return ''
}

// 保存された全体生産計画を取得
const fetchComprehensivePlan = async () => {
  // まずキャッシュをチェック
  const cachedPlan = sessionStorage.getItem('comprehensivePlan')
  if (cachedPlan) {
    try {
      const parsedPlan = JSON.parse(cachedPlan)
      comprehensivePlan.value = parsedPlan
      
      // スケジュールデータを展開
      generatedSchedule.value = []
      if (parsedPlan.products) {
        parsedPlan.products.forEach(product => {
          if (product.schedules) {
            product.schedules.forEach(schedule => {
              generatedSchedule.value.push({
                ...schedule,
                customer_name: product.customer_name,
                display_string: product.display_string,
                production_deadline: product.production_deadline,
                delivery_date: product.delivery_date
              })
            })
          }
        })
      }
      
      // プレス計画も更新（データがある場合のみ）
      if (parsedPlan.total_schedules_count > 0) {
        await loadPressScheduleFromPlan()
      }
      
      console.log('全体生産計画をキャッシュから読み込みました')
      return
    } catch (error) {
      console.error('キャッシュの読み込みに失敗しました:', error)
      // キャッシュが壊れている場合は削除
      sessionStorage.removeItem('comprehensivePlan')
    }
  }

  // キャッシュがない場合はAPIから取得
  loadingComprehensive.value = true
  loadingMessage.value = '全体生産計画を読み込み中...'

  try {
    const response = await api.get('/schedule/comprehensive-production-plan', {
      params: {
        working_hours: workingHours.value
      }
    })

    if (response.data.success) {
      comprehensivePlan.value = response.data
      
      // キャッシュに保存
      sessionStorage.setItem('comprehensivePlan', JSON.stringify(response.data))

      // スケジュールデータを展開
      generatedSchedule.value = []
      if (response.data.products) {
        response.data.products.forEach(product => {
          if (product.schedules) {
            product.schedules.forEach(schedule => {
              generatedSchedule.value.push({
                ...schedule,
                customer_name: product.customer_name,
                display_string: product.display_string,
                production_deadline: product.production_deadline,
                delivery_date: product.delivery_date
              })
            })
          }
        })
      }
      
      // プレス計画も更新（データがある場合のみ）
      if (response.data.total_schedules_count > 0) {
          await loadPressScheduleFromPlan()
      }
    }
  } catch (error) {
    console.error('Failed to fetch comprehensive plan:', error)
  } finally {
    loadingComprehensive.value = false
    loadingMessage.value = '読み込み中...'
  }
}

onMounted(() => {
  fetchComprehensivePlan()
  loadProgressSchedule2()
})

// 全体生産計画を計算
const generateComprehensivePlan = async () => {
  if (!confirm('全体生産計画を計算しますか？既存のスケジュールは削除されます。')) {
    return
  }

  loadingComprehensive.value = true
  loadingMessage.value = '全体生産計画を計算中...'

  try {
    const response = await api.post('/schedule/comprehensive-production-plan', {
      working_hours: workingHours.value
    }, {
      timeout: 120000  // 120秒に延長
    })

    if (response.data.success) {
      comprehensivePlan.value = response.data
      
      // キャッシュに保存
      sessionStorage.setItem('comprehensivePlan', JSON.stringify(response.data))

      // スケジュールデータを展開（製品ごとのスケジュールをフラットな配列に変換）
      generatedSchedule.value = []
      response.data.products.forEach(product => {
        product.schedules.forEach(schedule => {
          generatedSchedule.value.push({
            ...schedule,
            customer_name: product.customer_name,
            display_string: product.display_string,
            production_deadline: product.production_deadline,
            delivery_date: product.delivery_date
          })
        })
      })

      showError(response.data.message, '成功')

      // プレス計画と進捗確認を更新
      await loadPressScheduleFromPlan()
    }
  } catch (error) {
    console.error('Failed to generate comprehensive plan:', error)
    const errorDetail = error.response?.data?.detail || error.message
    showError('全体生産計画の計算に失敗しました:\n\n' + errorDetail, '全体生産計画エラー')
  } finally {
    loadingComprehensive.value = false
    loadingMessage.value = '読み込み中...'
  }
}

// 製品ごとの全体生産計画フィルタリング
const filteredComprehensivePlan = computed(() => {
  if (!comprehensivePlan.value.products) return []

  return comprehensivePlan.value.products.filter(product => {
    const customerMatch = !searchComprehensive.value.customer_name ||
      (product.customer_name && product.customer_name.toLowerCase().includes(searchComprehensive.value.customer_name.toLowerCase()))
    const productMatch = !searchComprehensive.value.product_code ||
      (product.product_code && product.product_code.toLowerCase().includes(searchComprehensive.value.product_code.toLowerCase()))
    return customerMatch && productMatch
  })
})

// 日付の差分（日数）を計算
const getDaysDifference = (dateStr) => {
  if (!dateStr) return '-'
  
  try {
    let targetDate
    
    // Check for YYYY-MM-DD format (backend response)
    if (typeof dateStr === 'string' && dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
       const [year, month, day] = dateStr.split('-').map(Number)
       targetDate = new Date(year, month - 1, day)
    } 
    // Check for dd/mm/yyyy format
    else if (typeof dateStr === 'string' && dateStr.includes('/') && !dateStr.includes(':')) {
       const parts = dateStr.split('/')
       if (parts.length === 3) {
         targetDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]))
       }
    }
    
    // Fallback
    if (!targetDate || isNaN(targetDate.getTime())) {
        targetDate = new Date(dateStr)
    }

    if (isNaN(targetDate.getTime())) return '-'

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    // Reset time part of targetDate to compare dates only
    const targetDay = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate())
    
    // 差分（ミリ秒）を計算
    const diffTime = targetDay - today
    // 日数に変換（切り上げ）
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays > 0) {
      return `+${diffDays}`
    } else {
      return `${diffDays}`
    }
  } catch (error) {
    console.error('Failed to calculate days difference:', error)
    return '-'
  }
}

// タスクが遅れているかどうかを判定
const isTaskOverdue = (task) => {
  if (!task.production_deadline) return false

  try {
    // production_deadline format: "dd/mm/yyyy HH:MM"
    const parts = task.production_deadline.split(' ')
    const dateParts = parts[0].split('/')
    const timeParts = parts[1] ? parts[1].split(':') : ['23', '59']

    // Create Date object (month is 0-indexed in JavaScript)
    const deadlineDate = new Date(
      parseInt(dateParts[2]), // year
      parseInt(dateParts[1]) - 1, // month (0-indexed)
      parseInt(dateParts[0]), // day
      parseInt(timeParts[0]), // hour
      parseInt(timeParts[1]) // minute
    )

    const now = new Date()
    return now > deadlineDate
  } catch (error) {
    console.error('Failed to parse production deadline:', task.production_deadline, error)
    return false
  }
}

// プレスセットが不完全かどうかを判定
const isPressSetIncomplete = (product, processData) => {
  if (!processData || !processData.name) return false
  const processName = processData.name

  // PRESS X/Y の形式かチェック (スペース許容)
  const match = processName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
  if (!match) return false

  const denominator = parseInt(match[2], 10)
  
  // 分母が0以下の場合は不正とみなす（あるいは無視）
  if (denominator <= 0) return true

  // 同じ製品の全工程を確認
  // process_1 〜 process_20 をスキャン
  const existingParts = new Set()
  
  for (let i = 1; i <= 20; i++) {
    const pData = product[`process_${i}`]
    if (pData && pData.name) {
      const pName = pData.name
      const pMatch = pName.match(/^PRESS\s*(\d+)\/(\d+)$/i)
      if (pMatch) {
        const pNum = parseInt(pMatch[1], 10)
        const pDenom = parseInt(pMatch[2], 10)
        // 分母が一致するものだけを対象にする
        if (pDenom === denominator) {
          existingParts.add(pNum)
        }
      }
    }
  }

  // 1 〜 denominator まで全て揃っているかチェック
  for (let i = 1; i <= denominator; i++) {
    if (!existingParts.has(i)) {
      return true // 欠けているものがある
    }
  }

  return false // 全て揃っている
}

onMounted(() => {
  // プレス計画を自動読み込み（進捗確認データも同時に生成される）
  loadPressScheduleFromPlan()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.tabs {
  display: flex;
  gap: var(--spacing-sm);
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  padding: var(--spacing-md) var(--spacing-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--background-hover);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.table-scroll-container {
  overflow-x: auto;
  max-width: 100%;
}

.process-table {
  min-width: 2200px;
}

.process-table th,
.process-table td {
  min-width: 85px;
  padding: 6px 4px;
  font-size: var(--font-size-sm);
}

.process-table th {
  white-space: nowrap;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 100px !important;
  white-space: nowrap;
}

.sticky-col-2 {
  position: sticky;
  left: 100px;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 100px !important;
  white-space: nowrap;
}

.sticky-col-3 {
  position: sticky;
  left: 200px;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 90px !important;
  white-space: normal;
}

.sticky-col-4 {
  position: sticky;
  left: 290px;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 100px !important;
  white-space: normal;
}

.sticky-col-5 {
  position: sticky;
  left: 390px;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 90px !important;
  white-space: nowrap;
}

.process-table thead .sticky-col,
.process-table thead .sticky-col-2,
.process-table thead .sticky-col-3,
.process-table thead .sticky-col-4,
.process-table thead .sticky-col-5 {
  background: #f8f9fa;
}

.clickable-cell {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-cell:hover {
  background-color: #e3f2fd;
}

.process-cell {
  white-space: pre-line;
  text-align: center;
  font-size: 10px;
  line-height: 1.25;
  max-width: 85px;
  word-break: normal;
  overflow-wrap: break-word;
  vertical-align: top;
  padding: 4px 2px;
}

.process-time-info {
  font-size: 0.85em;
  color: #666;
  margin-top: 2px;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

/* 工場稼働時間（タブ上部） */
.working-hours-top {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: #f8f9fa;
  border-radius: 8px;
  width: fit-content;
}

.working-hours-top .working-hours-label {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.working-hours-input-compact {
  width: 80px;
  font-size: var(--font-size-lg);
  text-align: center;
  padding: 6px var(--spacing-sm);
  border: 2px solid var(--border);
  border-radius: 6px;
}

/* 生産計画タブのスタイル */
.working-hours-section {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  padding: var(--spacing-xl);
  background: #f8f9fa;
  border-radius: 12px;
}

.working-hours-label {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.working-hours-input {
  width: 200px;
  font-size: var(--font-size-2xl);
  text-align: center;
  padding: var(--spacing-md);
  border: 2px solid var(--border);
  border-radius: 8px;
}

.calculate-section {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.calculate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 24px 60px;
  font-size: var(--font-size-xl);
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-md);
}

.calculate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.calculate-icon {
  font-size: var(--font-size-2xl);
}

.progress-section {
  margin: var(--spacing-2xl) 0;
  padding: var(--spacing-xl);
  background: #f8f9fa;
  border-radius: 12px;
}

.progress-bar-container {
  width: 100%;
  height: 30px;
  background: #e0e0e0;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: var(--spacing-md);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.production-plan-results {
  margin-top: var(--spacing-2xl);
}

/* モーダルスタイル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  min-width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.confirm-modal {
  min-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: var(--font-size-xl);
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--font-size-2xl);
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: var(--spacing-xl);
}

.modal-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
}

/* 生産計画タブの追加スタイル */
.clickable-process {
  cursor: pointer;
  color: var(--primary);
  transition: all 0.2s;
}

.clickable-process:hover {
  background-color: #e3f2fd;
  font-weight: 600;
}

.delayed-datetime {
  color: #d32f2f;
  font-weight: bold;
}

.warning-datetime {
  color: #f57c00;
  font-weight: bold;
}

.normal-green-datetime {
  color: #388e3c;
  font-weight: bold;
}

/* プレス計画タブのスタイル */
.press-schedule-container {
  margin-top: var(--spacing-xl);
}

.press-schedule-table {
  min-width: 1400px;
}

.press-schedule-table th,
.press-schedule-table td {
  min-width: 150px;
  padding: 8px;
  font-size: var(--font-size-sm);
  vertical-align: top;
}

.sticky-col-press {
  position: sticky;
  left: 0;
  background: white;
  z-index: 3;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  min-width: 120px !important;
  white-space: nowrap;
  font-weight: 600;
}

.press-schedule-table thead .sticky-col-press {
  background: #f8f9fa;
}

.machine-cell {
  font-weight: 600;
  background: #f8f9fa;
}

.schedule-cell {
  border: 1px solid var(--border);
  background: white;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  background: #e3f2fd;
  border-left: 3px solid #1976d2;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  line-height: 1.4;
}

.task-item-split {
  background: #fff3e0;
  border-left: 3px solid #f57c00;
}

.task-item-overdue {
  background: #ffebee;
  border-left: 3px solid #d32f2f;
}

.task-item-overdue .task-header {
  color: #c62828;
}

.task-item-setup {
  background: #d7ccc8;
  border-left: 3px solid #795548;
}

.task-item-setup .task-header {
  color: #4e342e;
}

.task-item-overdue .task-time-info {
  color: #d32f2f;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-weight: 600;
  color: #1565c0;
  flex-wrap: wrap;
  gap: 4px;
}

.split-badge {
  display: inline-block;
  background: #ff9800;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 700;
  margin-left: 4px;
}

.task-time {
  font-size: 10px;
  color: #424242;
  font-weight: normal;
}

.task-time-info {
  font-size: 10px;
  color: #f57c00;
  font-weight: 600;
  margin-bottom: 4px;
  text-align: center;
}

.task-process-name {
  font-size: 11px;
  color: #2e7d32;
  font-weight: 600;
  margin-bottom: 4px;
  padding: 2px 4px;
  background: #e8f5e9;
  border-radius: 3px;
  display: inline-block;
}

.task-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: #424242;
}

.task-details div {
  font-size: 10px;
}

.empty-cell {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--spacing-md);
}

/* 全工程スケジュールタブのスタイル */
.info-box {
  background: #e3f2fd;
  border-left: 4px solid #1976d2;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  border-radius: 4px;
}

.info-box p {
  margin: 4px 0;
  font-size: var(--font-size-sm);
  color: #424242;
}

.schedule-detail-table {
  font-size: var(--font-size-sm);
}

.schedule-detail-table th,
.schedule-detail-table td {
  padding: 8px;
  white-space: nowrap;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-scheduled {
  background: #e3f2fd;
  color: #1565c0;
}

.status-waiting {
  background: #fff3e0;
  color: #e65100;
}

.status-in_progress {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-completed {
  background: #f3e5f5;
  color: #6a1b9a;
}

.schedule-row-waiting {
  background-color: #fff8e1;
}

.schedule-row-progress {
  background-color: #e8f5e9;
}

.schedule-row-completed {
  background-color: #f3e5f5;
  opacity: 0.7;
}

.setup-time-info {
  font-size: 10px;
  color: #666;
  margin-top: 4px;
  line-height: 1.2;
}

.quantity-split {
  color: #FF6F00 !important;
  font-weight: bold !important;
}
</style>
