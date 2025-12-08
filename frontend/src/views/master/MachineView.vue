<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">機械リストマスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>機械登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">機械番号</label>
              <input v-model="form.machine_no" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">機械種類</label>
              <select v-model="form.machine_type" class="form-input" required>
                <option value="">選択してください</option>
                <option value="PRESS">PRESS</option>
                <option value="TAP">TAP</option>
                <option value="BARREL">BARREL</option>
              </select>
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">工場名</label>
              <AutocompleteInput
                v-model="form.factory_id"
                endpoint="/master/autocomplete/factories"
                display-field="name"
                value-field="id"
                placeholder="工場名を入力..."
                required
              />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>機械一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="機械番号で検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>機械番号</th>
              <th>機械種類</th>
              <th>工場名</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in machines" :key="item.machine_list_id">
              <td>{{ item.machine_list_id }}</td>
              <td>{{ item.machine_no }}</td>
              <td>{{ item.machine_type || '-' }}</td>
              <td>{{ item.factory_name || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="machines.length === 0" class="empty-state">
          <p>機械データがありません</p>
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
import api from '../../utils/api'

const form = ref({
  machine_no: '',
  machine_type: '',
  factory_id: null,
})

const machines = ref([])
const searchQuery = ref('')

const loadMachines = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/machines', { params })
    machines.value = response.data
  } catch (error) {
    console.error('Failed to load machines:', error)
    alert('機械の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/machines', form.value)
    alert('機械の登録に成功しました')
    form.value = {
      machine_no: '',
      machine_type: '',
      factory_id: null,
    }
    await loadMachines()
  } catch (error) {
    console.error('Failed to create machine:', error)
    alert('機械の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadMachines(searchQuery.value)
}

onMounted(() => {
  loadMachines()
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
