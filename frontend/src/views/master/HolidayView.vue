<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">休日マスター</h1>

      <!-- タブナビゲーション -->
      <div class="tabs" style="margin-bottom: var(--spacing-lg)">
        <button
          @click="activeTab = 'holidays'"
          :class="{ active: activeTab === 'holidays' }"
          class="tab-btn"
        >
          休日登録
        </button>
        <button
          @click="activeTab = 'holiday-types'"
          :class="{ active: activeTab === 'holiday-types' }"
          class="tab-btn"
        >
          休日種別管理
        </button>
      </div>

      <!-- 休日登録タブ -->
      <div v-if="activeTab === 'holidays'">
        <!-- 休日登録フォーム -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>休日登録</h2>
        <form @submit.prevent="handleSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
          <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">休日日付</label>
            <input v-model="form.date_holiday" class="form-input" type="text" placeholder="DD/MM/YYYY" required />
          </div>
          <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
            <label class="form-label" style="margin-bottom: 0;">休日種別</label>
            <select v-model.number="form.holiday_type_id" class="form-input" required>
              <option value="">種別を選択</option>
              <option v-for="type in holidayTypes" :key="type.holiday_type_id" :value="type.holiday_type_id">
                {{ type.date_type }}
              </option>
            </select>
          </div>
          <div>
            <button type="submit" class="btn btn-primary">登録</button>
          </div>
        </form>
      </div>

      <!-- 休日一覧 -->
      <div class="card">
        <h2>休日一覧</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>休日日付</th>
              <th>休日種別</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in holidays" :key="item.calendar_id">
              <td>{{ item.calendar_id }}</td>
              <td>{{ formatDateForDisplay(item.date_holiday) }}</td>
              <td>{{ item.date_type }}</td>
              <td>
                <button @click="handleDelete(item.calendar_id)" class="btn btn-danger btn-sm">
                  削除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="holidays.length === 0" class="empty-state">
          <p>休日データがありません</p>
        </div>
      </div>
      </div>

      <!-- 休日種別管理タブ -->
      <div v-if="activeTab === 'holiday-types'">
        <!-- 休日種別登録フォーム -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>休日種別登録</h2>
          <form @submit.prevent="handleHolidayTypeSubmit" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">休日種別名</label>
              <input v-model="holidayTypeForm.date_type" class="form-input" type="text" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </form>
        </div>

        <!-- 休日種別一覧 -->
        <div class="card">
          <h2>休日種別一覧</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>休日種別名</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="type in holidayTypes" :key="type.holiday_type_id">
                <td>{{ type.holiday_type_id }}</td>
                <td>{{ type.date_type }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="holidayTypes.length === 0" class="empty-state">
            <p>休日種別データがありません</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import api from '../../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../../utils/dateFormat'

const activeTab = ref('holidays')

const form = ref({
  date_holiday: getTodayFormatted(),
  holiday_type_id: '',
})

const holidayTypeForm = ref({
  date_type: '',
})

const holidayTypes = ref([])
const holidays = ref([])

const loadHolidayTypes = async () => {
  try {
    const response = await api.get('/schedule/holiday-types')
    holidayTypes.value = response.data
  } catch (error) {
    console.error('Failed to load holiday types:', error)
  }
}

const loadHolidays = async () => {
  try {
    const response = await api.get('/schedule/calendar')
    holidays.value = response.data
  } catch (error) {
    console.error('Failed to load holidays:', error)
    alert('休日の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  try {
    // DD/MM/YYYY形式をYYYY-MM-DD形式に変換してAPIに送信
    const submitData = {
      ...form.value,
      date_holiday: formatDateForApi(form.value.date_holiday)
    }

    await api.post('/schedule/calendar', submitData)
    alert('休日の登録に成功しました')
    form.value = {
      date_holiday: getTodayFormatted(),
      holiday_type_id: '',
    }
    await loadHolidays()
  } catch (error) {
    console.error('Failed to create holiday:', error)
    alert('休日の登録に失敗しました')
  }
}

const handleDelete = async (id) => {
  if (!confirm('この休日を削除しますか？')) {
    return
  }

  try {
    await api.delete(`/schedule/calendar/${id}`)
    alert('休日の削除に成功しました')
    await loadHolidays()
  } catch (error) {
    console.error('Failed to delete holiday:', error)
    alert('休日の削除に失敗しました')
  }
}

const handleHolidayTypeSubmit = async () => {
  try {
    await api.post('/schedule/holiday-types', holidayTypeForm.value)
    alert('休日種別の登録に成功しました')
    holidayTypeForm.value = {
      date_type: '',
    }
    await loadHolidayTypes()
  } catch (error) {
    console.error('Failed to create holiday type:', error)
    alert('休日種別の登録に失敗しました')
  }
}

onMounted(() => {
  loadHolidayTypes()
  loadHolidays()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
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
</style>
