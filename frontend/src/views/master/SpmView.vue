<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">生産プレス機設定マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>生産プレス機設定登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">製品コード</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="code"
                value-field="id"
                placeholder="製品コードを入力..."
                required
              />
            </div>
            <div style="width: 150px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">工程名</label>
              <AutocompleteInput
                v-model="form.process_name"
                endpoint="/master/autocomplete/process-names"
                display-field="name"
                value-field="name"
                placeholder="工程名を入力..."
                required
              />
            </div>
            <div style="width: 120px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">プレス番号</label>
              <AutocompleteInput
                v-model="form.press_no"
                endpoint="/master/autocomplete/machines"
                display-field="machine_no"
                value-field="machine_no"
                placeholder="プレス番号を入力..."
                :filter-params="{ machine_type: 'PRESS' }"
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">サイクルタイム</label>
              <input v-model.number="form.cycle_time" class="form-input" type="number" step="0.01" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>生産プレス機設定一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="製品コードで検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>製品コード</th>
              <th>工程名</th>
              <th>プレス番号</th>
              <th>サイクルタイム</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in spmSettings" :key="item.spm_id">
              <td>{{ item.spm_id }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.process_name }}</td>
              <td>{{ item.press_no }}</td>
              <td>{{ item.cycle_time }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="spmSettings.length === 0" class="empty-state">
          <p>生産プレス機設定データがありません</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import CopyableText from '../../components/common/CopyableText.vue'
import api from '../../utils/api'

const form = ref({
  product_id: null,
  process_name: '',
  press_no: '',
  cycle_time: null,
})

const spmSettings = ref([])
const searchQuery = ref('')

const loadSpmSettings = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/spm', { params })
    spmSettings.value = response.data
  } catch (error) {
    console.error('Failed to load SPM settings:', error)
    alert('SPM設定の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('製品を選択してください')
    return
  }

  try {
    await api.post('/master/spm', form.value)
    alert('SPM設定の登録に成功しました')
    form.value = {
      product_id: null,
      process_name: '',
      press_no: '',
      cycle_time: null,
    }
    await loadSpmSettings()
  } catch (error) {
    console.error('Failed to create SPM settings:', error)
    alert('SPM設定の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadSpmSettings(searchQuery.value)
}

onMounted(() => {
  loadSpmSettings()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
