<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">工程名マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>工程名登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">工程名</label>
              <input v-model="form.process_name" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">種別</label>
              <div style="display: flex; gap: 16px; align-items: center; height: 34px;">
                <label style="display: flex; align-items: center; gap: 4px;">
                  <input v-model="form.day_or_spm" type="radio" :value="true" />
                  <span>SPM</span>
                </label>
                <label style="display: flex; align-items: center; gap: 4px;">
                  <input v-model="form.day_or_spm" type="radio" :value="false" />
                  <span>Day</span>
                </label>
              </div>
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>工程名一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="工程名で検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>工程名</th>
              <th>種別</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in processNames" :key="item.process_name_id">
              <td>{{ item.process_name_id }}</td>
              <td>{{ item.process_name }}</td>
              <td>
                <span :class="item.day_or_spm ? 'type-spm' : 'type-day'">
                  {{ item.day_or_spm ? 'SPM' : 'Day' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="processNames.length === 0" class="empty-state">
          <p>工程名データがありません</p>
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

const form = ref({
  process_name: '',
  day_or_spm: true,
})

const processNames = ref([])
const searchQuery = ref('')

const loadProcessNames = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/process-names', { params })
    processNames.value = response.data
  } catch (error) {
    console.error('Failed to load process names:', error)
    alert('工程名の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/process-names', form.value)
    alert('工程名の登録に成功しました')
    form.value = {
      process_name: '',
      day_or_spm: true,
    }
    await loadProcessNames()
  } catch (error) {
    console.error('Failed to create process name:', error)
    alert('工程名の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadProcessNames(searchQuery.value)
}

onMounted(() => {
  loadProcessNames()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.type-spm {
  color: var(--primary);
  font-weight: 600;
}

.type-day {
  color: var(--warning);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
